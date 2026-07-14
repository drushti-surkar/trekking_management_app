import os

from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_security import auth_required, roles_required, current_user
from flask_security.utils import hash_password

from extensions import db
from models import Trek, Booking
from utils import recalc_available_slots
from cache import cache_get, cache_set, invalidate_open_treks, OPEN_TREKS_KEY

trekker_bp = Blueprint("trekker", __name__, url_prefix="/api/trekker")


def trek_dict(t, user_booking=None):
    return {
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration_days": t.duration_days,
        "available_slots": t.available_slots,
        "total_slots": t.total_slots,
        "status": t.status,
        "start_date": t.start_date.isoformat() if t.start_date else None,
        "end_date": t.end_date.isoformat() if t.end_date else None,
        # is the current trekker already actively booked on this trek?
        "already_booked": bool(user_booking and user_booking.status in ("Booked", "Completed")),
    }


def booking_dict(b):
    t = b.trek
    return {
        "id": b.id,
        "trek_id": b.trek_id,
        "trek_name": t.name if t else None,
        "location": t.location if t else None,
        "difficulty": t.difficulty if t else None,
        "trek_status": t.status if t else None,
        "start_date": t.start_date.isoformat() if t and t.start_date else None,
        "status": b.status,
        "payment_status": b.payment_status,
        "booking_date": b.booking_date.isoformat() if b.booking_date else None,
    }


@trekker_bp.get("/treks")
@auth_required("token")
@roles_required("trekker")
def browse_treks():
    q = (request.args.get("q") or "").strip()
    difficulty = (request.args.get("difficulty") or "").strip()
    location = (request.args.get("location") or "").strip()
    max_duration = request.args.get("max_duration")

    no_filters = not (q or difficulty or location or max_duration)
    mine = {b.trek_id: b for b in current_user.bookings}

    if no_filters:
        items = cache_get(OPEN_TREKS_KEY)
        if items is None:
            treks = Trek.query.filter_by(status="Open").order_by(
                Trek.start_date.is_(None), Trek.start_date
            ).all()
            items = [trek_dict(t) for t in treks]
            cache_set(OPEN_TREKS_KEY, items)
        for it in items:
            b = mine.get(it["id"])
            it["already_booked"] = bool(b and b.status in ("Booked", "Completed"))
        return jsonify(items)

    # Filtered searches hit the DB directly
    query = Trek.query.filter_by(status="Open")
    if q:
        query = query.filter(Trek.name.ilike(f"%{q}%"))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if max_duration:
        try:
            query = query.filter(Trek.duration_days <= int(max_duration))
        except ValueError:
            pass

    treks = query.order_by(Trek.start_date.is_(None), Trek.start_date).all()
    return jsonify([trek_dict(t, mine.get(t.id)) for t in treks])


@trekker_bp.post("/bookings")
@auth_required("token")
@roles_required("trekker")
def book():
    d = request.get_json(silent=True) or {}
    trek_id = d.get("trek_id")
    trek = Trek.query.get(trek_id) if trek_id else None
    if not trek:
        return jsonify(error="Trek not found."), 404

    if trek.status != "Open":
        return jsonify(error="This trek is not open for booking."), 400

    existing = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id).first()
    if existing and existing.status in ("Booked", "Completed"):
        return jsonify(error="You have already booked this trek."), 409

    # Capacity check (recompute from live bookings to be safe)
    recalc_available_slots(trek)
    if trek.available_slots <= 0:
        return jsonify(error="This trek is full."), 400

    if existing:  # re-activate a previously cancelled booking (unique user+trek)
        existing.status = "Booked"
        booking = existing
    else:
        booking = Booking(user_id=current_user.id, trek_id=trek.id, status="Booked")
        db.session.add(booking)

    db.session.flush()
    recalc_available_slots(trek)
    db.session.commit()
    invalidate_open_treks()  # slots changed
    return jsonify(booking_dict(booking)), 201


@trekker_bp.get("/bookings")
@auth_required("token")
@roles_required("trekker")
def my_bookings():
    rows = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.id.desc())
        .all()
    )
    return jsonify([booking_dict(b) for b in rows])


@trekker_bp.patch("/bookings/<int:booking_id>/cancel")
@auth_required("token")
@roles_required("trekker")
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        return jsonify(error="Not your booking."), 403
    if booking.status != "Booked":
        return jsonify(error="Only active bookings can be cancelled."), 400

    booking.status = "Cancelled"
    recalc_available_slots(booking.trek)
    db.session.commit()
    invalidate_open_treks()  # a seat freed up
    return jsonify(booking_dict(booking))


@trekker_bp.get("/profile")
@auth_required("token")
@roles_required("trekker")
def get_profile():
    return jsonify(name=current_user.name, email=current_user.email)


@trekker_bp.put("/profile")
@auth_required("token")
@roles_required("trekker")
def update_profile():
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    password = d.get("password") or ""

    if not name:
        return jsonify(error="Name is required."), 400
    current_user.name = name
    if password:
        if len(password) < 6:
            return jsonify(error="Password must be at least 6 characters."), 400
        current_user.password = hash_password(password)
        # rotate token so a password change invalidates old sessions
        db.session.add(current_user)

    db.session.commit()
    return jsonify(name=current_user.name, email=current_user.email)


@trekker_bp.post("/export")
@auth_required("token")
@roles_required("trekker")
def start_export():
    # Lazy import breaks the Flask <-> Celery import cycle
    from tasks import export_bookings_csv
    task = export_bookings_csv.delay(current_user.id)
    return jsonify(task_id=task.id), 202


@trekker_bp.get("/export/<task_id>/status")
@auth_required("token")
@roles_required("trekker")
def export_status(task_id):
    from celery_app import celery
    res = celery.AsyncResult(task_id)
    if res.successful():
        info = res.result or {}
        return jsonify(state="SUCCESS", filename=info.get("file"),
                       records=info.get("records"))
    if res.failed():
        return jsonify(state="FAILURE"), 200
    return jsonify(state=res.state), 200  # PENDING / STARTED


@trekker_bp.get("/export/download/<path:fname>")
@auth_required("token")
@roles_required("trekker")
def export_download(fname):
    # Only allow a trekker to download their own export file
    if not fname.startswith(f"booking_history_{current_user.id}_"):
        return jsonify(error="Not your export file."), 403
    export_dir = current_app.config["EXPORT_DIR"]
    if not os.path.exists(os.path.join(export_dir, fname)):
        return jsonify(error="File not found or expired."), 404
    return send_from_directory(export_dir, fname, as_attachment=True)
