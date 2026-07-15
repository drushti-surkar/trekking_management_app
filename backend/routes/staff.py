from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required, current_user

from extensions import db
from models import Trek, Booking
from utils import recalc_available_slots, complete_trek_bookings
from cache import invalidate_open_treks

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")

STAFF_TREK_STATUSES = {"Open", "Closed", "Completed"}

STAFF_BOOKING_STATUSES = {"Booked", "Completed", "Cancelled"}


def trek_dict(t):
    active = [b for b in t.bookings if b.status == "Booked"]
    return {
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration_days": t.duration_days,
        "total_slots": t.total_slots,
        "available_slots": t.available_slots,
        "status": t.status,
        "start_date": t.start_date.isoformat() if t.start_date else None,
        "end_date": t.end_date.isoformat() if t.end_date else None,
        "registered_count": len(active),
    }


def participant_dict(b):
    return {
        "booking_id": b.id,
        "user_name": b.user.name if b.user else None,
        "user_email": b.user.email if b.user else None,
        "status": b.status,
        "payment_status": b.payment_status,
        "booking_date": b.booking_date.isoformat() if b.booking_date else None,
    }


def _owned_trek_or_403(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        return None
    return trek


@staff_bp.get("/stats")
@auth_required("token")
@roles_required("staff")
def stats():
    treks = current_user.assigned_treks
    registered = sum(
        1 for t in treks for b in t.bookings if b.status == "Booked"
    )
    return jsonify(
        assigned_treks=len(treks),
        total_registered=registered,
        open_treks=sum(1 for t in treks if t.status == "Open"),
    )


@staff_bp.get("/treks")
@auth_required("token")
@roles_required("staff")
def my_treks():
    treks = Trek.query.filter_by(assigned_staff_id=current_user.id).order_by(Trek.id.desc()).all()
    return jsonify([trek_dict(t) for t in treks])


@staff_bp.get("/analytics")
@auth_required("token")
@roles_required("staff")
def analytics():
    from collections import defaultdict
    from datetime import date

    treks = current_user.assigned_treks
    my_bookings = [b for t in treks for b in t.bookings]
    active = [b for b in my_bookings if b.status in ("Booked", "Completed")]

    totals = {
        "treks": len(treks),
        "open_treks": sum(1 for t in treks if t.status == "Open"),
        "completed_treks": sum(1 for t in treks if t.status == "Completed"),
        "participants": len(active),
    }

    popular = []
    for t in treks:
        count = sum(1 for b in t.bookings if b.status in ("Booked", "Completed"))
        if count:
            popular.append({"name": t.name, "bookings": count})
    popular.sort(key=lambda x: x["bookings"], reverse=True)
    popular = popular[:5]

    difficulty = {"Easy": 0, "Moderate": 0, "Hard": 0}
    for t in treks:
        if t.difficulty in difficulty:
            difficulty[t.difficulty] += 1

    month_abbr = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    today = date.today()
    months = []
    y, m = today.year, today.month
    for i in range(5, -1, -1):
        mm, yy = m - i, y
        while mm <= 0:
            mm += 12
            yy -= 1
        months.append((yy, mm))
    bucket = defaultdict(int)
    for b in my_bookings:
        if b.booking_date:
            bucket[(b.booking_date.year, b.booking_date.month)] += 1
    monthly_trend = {
        "labels": [month_abbr[mm] for (_, mm) in months],
        "counts": [bucket.get((yy, mm), 0) for (yy, mm) in months],
    }

    status_breakdown = {
        "Booked": sum(1 for b in my_bookings if b.status == "Booked"),
        "Completed": sum(1 for b in my_bookings if b.status == "Completed"),
        "Cancelled": sum(1 for b in my_bookings if b.status == "Cancelled"),
    }

    return jsonify(
        totals=totals, popular_treks=popular, difficulty=difficulty,
        monthly_trend=monthly_trend, status_breakdown=status_breakdown,
    )


@staff_bp.patch("/treks/<int:trek_id>/slots")
@auth_required("token")
@roles_required("staff")
def update_slots(trek_id):
    trek = _owned_trek_or_403(trek_id)
    if not trek:
        return jsonify(error="You can only manage treks assigned to you."), 403

    d = request.get_json(silent=True) or {}
    try:
        new_total = int(d.get("total_slots"))
    except (TypeError, ValueError):
        return jsonify(error="total_slots must be a number."), 400

    booked = sum(1 for b in trek.bookings if b.status == "Booked")
    if new_total < booked:
        return jsonify(error=f"Capacity cannot be below {booked} current bookings."), 400
    if new_total <= 0:
        return jsonify(error="Capacity must be positive."), 400

    trek.total_slots = new_total
    recalc_available_slots(trek)
    db.session.commit()
    invalidate_open_treks()
    return jsonify(trek_dict(trek))


@staff_bp.patch("/treks/<int:trek_id>/status")
@auth_required("token")
@roles_required("staff")
def update_status(trek_id):
    trek = _owned_trek_or_403(trek_id)
    if not trek:
        return jsonify(error="You can only manage treks assigned to you."), 403

    d = request.get_json(silent=True) or {}
    status = d.get("status")
    if status not in STAFF_TREK_STATUSES:
        return jsonify(error=f"Status must be one of {sorted(STAFF_TREK_STATUSES)}."), 400

    trek.status = status
    if status == "Completed":
        complete_trek_bookings(trek)
    db.session.commit()
    invalidate_open_treks()
    return jsonify(trek_dict(trek))


@staff_bp.get("/treks/<int:trek_id>/participants")
@auth_required("token")
@roles_required("staff")
def participants(trek_id):
    trek = _owned_trek_or_403(trek_id)
    if not trek:
        return jsonify(error="You can only view participants of your treks."), 403
    rows = sorted(trek.bookings, key=lambda b: b.id)
    return jsonify([participant_dict(b) for b in rows])


@staff_bp.patch("/bookings/<int:booking_id>/status")
@auth_required("token")
@roles_required("staff")
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if not booking.trek or booking.trek.assigned_staff_id != current_user.id:
        return jsonify(error="You can only manage participants of your treks."), 403

    d = request.get_json(silent=True) or {}
    status = d.get("status")
    if status not in STAFF_BOOKING_STATUSES:
        return jsonify(error=f"Status must be one of {sorted(STAFF_BOOKING_STATUSES)}."), 400

    booking.status = status
    recalc_available_slots(booking.trek)
    db.session.commit()
    return jsonify(participant_dict(booking))
