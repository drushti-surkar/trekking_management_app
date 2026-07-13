"""Trekker (User) API: browse/filter open treks, book, view history,
cancel bookings, and update own profile.
"""
from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required, current_user
from flask_security.utils import hash_password

from extensions import db
from models import Trek, Booking
from utils import recalc_available_slots

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


# ----------------------------------------------------------------------------
# Browse / filter open treks
# ----------------------------------------------------------------------------
@trekker_bp.get("/treks")
@auth_required("token")
@roles_required("trekker")
def browse_treks():
    q = (request.args.get("q") or "").strip()
    difficulty = (request.args.get("difficulty") or "").strip()
    location = (request.args.get("location") or "").strip()
    max_duration = request.args.get("max_duration")

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

    # Map this user's bookings so we can flag already-booked treks
    mine = {b.trek_id: b for b in current_user.bookings}
    return jsonify([trek_dict(t, mine.get(t.id)) for t in treks])


# ----------------------------------------------------------------------------
# Book a trek
# ----------------------------------------------------------------------------
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
    return jsonify(booking_dict(booking)), 201


# ----------------------------------------------------------------------------
# Booking history
# ----------------------------------------------------------------------------
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
    return jsonify(booking_dict(booking))


# ----------------------------------------------------------------------------
# Profile
# ----------------------------------------------------------------------------
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
