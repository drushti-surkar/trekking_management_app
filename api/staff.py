"""Trek Staff API: dashboard + operations limited to the staff member's
own assigned treks. Every trek/booking action verifies ownership.
"""
from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required, current_user

from extensions import db
from models import Trek, Booking
from utils import recalc_available_slots

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")

# Statuses a staff member is allowed to set on their trek.
# (Pending/Approved are admin-side lifecycle stages.)
STAFF_TREK_STATUSES = {"Open", "Closed", "Completed"}
# Statuses a staff member can set on a participant's booking.
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
    """Return the trek only if it is assigned to the current staff member."""
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        return None
    return trek


# ----------------------------------------------------------------------------
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
    db.session.commit()
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
    recalc_available_slots(booking.trek)  # freeing/occupying a seat
    db.session.commit()
    return jsonify(participant_dict(booking))
