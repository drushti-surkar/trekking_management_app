from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required

from extensions import db, security
from models import User, Role, Trek, Booking, StaffProfile
from utils import complete_trek_bookings
from cache import invalidate_open_treks

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

DIFFICULTIES = {"Easy", "Moderate", "Hard"}
TREK_STATUSES = {"Pending", "Approved", "Open", "Closed", "Completed"}


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
        "assigned_staff_id": t.assigned_staff_id,
        "assigned_staff_name": t.assigned_staff.name if t.assigned_staff else None,
        "booked_count": len(active),
    }


def user_dict(u):
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.roles[0].name if u.roles else None,
        "active": u.active,
    }


def staff_dict(u):
    p = u.staff_profile
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "active": u.active,
        "contact_number": p.contact_number if p else None,
        "status": p.status if p else None,
        "assigned_treks": len(u.assigned_treks),
    }


def booking_dict(b):
    return {
        "id": b.id,
        "user_name": b.user.name if b.user else None,
        "user_email": b.user.email if b.user else None,
        "trek_name": b.trek.name if b.trek else None,
        "status": b.status,
        "payment_status": b.payment_status,
        "booking_date": b.booking_date.isoformat() if b.booking_date else None,
    }


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@admin_bp.get("/stats")
@auth_required("token")
@roles_required("admin")
def stats():
    staff_role = security.datastore.find_role("staff")
    trekker_role = security.datastore.find_role("trekker")
    return jsonify(
        total_treks=Trek.query.count(),
        total_users=User.query.filter(User.roles.contains(trekker_role)).count(),
        total_staff=User.query.filter(User.roles.contains(staff_role)).count(),
        total_bookings=Booking.query.count(),
    )


@admin_bp.get("/treks")
@auth_required("token")
@roles_required("admin")
def list_treks():
    q = (request.args.get("q") or "").strip()
    query = Trek.query
    if q:
        like = f"%{q}%"
        if q.isdigit():
            query = query.filter((Trek.name.ilike(like)) | (Trek.id == int(q)))
        else:
            query = query.filter((Trek.name.ilike(like)) | (Trek.location.ilike(like)))
    treks = query.order_by(Trek.id.desc()).all()
    return jsonify([trek_dict(t) for t in treks])


@admin_bp.post("/treks")
@auth_required("token")
@roles_required("admin")
def create_trek():
    d = request.get_json(silent=True) or {}
    err = _validate_trek(d, creating=True)
    if err:
        return jsonify(error=err), 400

    trek = Trek(
        name=d["name"].strip(),
        location=d["location"].strip(),
        difficulty=d["difficulty"],
        duration_days=int(d["duration_days"]),
        total_slots=int(d["total_slots"]),
        available_slots=int(d["total_slots"]),
        status=d.get("status", "Pending"),
        assigned_staff_id=d.get("assigned_staff_id") or None,
        start_date=_parse_date(d.get("start_date")),
        end_date=_parse_date(d.get("end_date")),
    )
    db.session.add(trek)
    db.session.commit()
    invalidate_open_treks()
    return jsonify(trek_dict(trek)), 201


@admin_bp.put("/treks/<int:trek_id>")
@auth_required("token")
@roles_required("admin")
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    d = request.get_json(silent=True) or {}
    err = _validate_trek(d, creating=False)
    if err:
        return jsonify(error=err), 400

    if "name" in d:
        trek.name = d["name"].strip()
    if "location" in d:
        trek.location = d["location"].strip()
    if "difficulty" in d:
        trek.difficulty = d["difficulty"]
    if "duration_days" in d:
        trek.duration_days = int(d["duration_days"])
    if "total_slots" in d:
        new_total = int(d["total_slots"])
        booked = len([b for b in trek.bookings if b.status == "Booked"])
        if new_total < booked:
            return jsonify(error=f"Total slots cannot be less than {booked} current bookings."), 400
        trek.available_slots = new_total - booked
        trek.total_slots = new_total
    if "status" in d:
        trek.status = d["status"]
        if d["status"] == "Completed":
            complete_trek_bookings(trek)  # roll active bookings to Completed
    if "assigned_staff_id" in d:
        trek.assigned_staff_id = d["assigned_staff_id"] or None
    if "start_date" in d:
        trek.start_date = _parse_date(d.get("start_date"))
    if "end_date" in d:
        trek.end_date = _parse_date(d.get("end_date"))

    db.session.commit()
    invalidate_open_treks()
    return jsonify(trek_dict(trek))


@admin_bp.delete("/treks/<int:trek_id>")
@auth_required("token")
@roles_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    invalidate_open_treks()
    return jsonify(message="Trek deleted."), 200


def _validate_trek(d, creating):
    required = ["name", "location", "difficulty", "duration_days", "total_slots"]
    if creating:
        for f in required:
            if d.get(f) in (None, ""):
                return f"Field '{f}' is required."
    if "difficulty" in d and d["difficulty"] not in DIFFICULTIES:
        return "Difficulty must be Easy, Moderate or Hard."
    if "status" in d and d["status"] not in TREK_STATUSES:
        return "Invalid trek status."
    for f in ("duration_days", "total_slots"):
        if f in d and d[f] not in (None, ""):
            try:
                if int(d[f]) <= 0:
                    return f"'{f}' must be a positive number."
            except (ValueError, TypeError):
                return f"'{f}' must be a number."
    if d.get("assigned_staff_id"):
        staff = User.query.get(d["assigned_staff_id"])
        if not staff or not any(r.name == "staff" for r in staff.roles):
            return "Assigned staff must be a valid staff member."
    return None


@admin_bp.get("/staff")
@auth_required("token")
@roles_required("admin")
def list_staff():
    q = (request.args.get("q") or "").strip()
    staff_role = security.datastore.find_role("staff")
    query = User.query.filter(User.roles.contains(staff_role))
    if q:
        like = f"%{q}%"
        if q.isdigit():
            query = query.filter((User.name.ilike(like)) | (User.id == int(q)))
        else:
            query = query.filter((User.name.ilike(like)) | (User.email.ilike(like)))
    return jsonify([staff_dict(u) for u in query.order_by(User.id).all()])


@admin_bp.post("/staff")
@auth_required("token")
@roles_required("admin")
def create_staff():
    from flask_security.utils import hash_password
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    email = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""
    contact = (d.get("contact_number") or "").strip()

    if not name or not email or not password:
        return jsonify(error="Name, email and password are required."), 400
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters."), 400

    ds = security.datastore
    if ds.find_user(email=email):
        return jsonify(error="An account with this email already exists."), 409

    user = ds.create_user(
        email=email, name=name,
        password=hash_password(password), roles=["staff"],
    )
    db.session.flush()
    db.session.add(StaffProfile(user_id=user.id, contact_number=contact, status="Active"))
    db.session.commit()
    return jsonify(staff_dict(user)), 201


@admin_bp.get("/users")
@auth_required("token")
@roles_required("admin")
def list_users():
    q = (request.args.get("q") or "").strip()
    trekker_role = security.datastore.find_role("trekker")
    query = User.query.filter(User.roles.contains(trekker_role))
    if q:
        like = f"%{q}%"
        if q.isdigit():
            query = query.filter((User.name.ilike(like)) | (User.id == int(q)))
        else:
            query = query.filter((User.name.ilike(like)) | (User.email.ilike(like)))
    return jsonify([user_dict(u) for u in query.order_by(User.id).all()])


@admin_bp.patch("/users/<int:user_id>/toggle-active")
@auth_required("token")
@roles_required("admin")
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if any(r.name == "admin" for r in user.roles):
        return jsonify(error="Cannot deactivate an admin."), 400
    user.active = not user.active
    db.session.commit()
    return jsonify(id=user.id, active=user.active)


@admin_bp.get("/bookings")
@auth_required("token")
@roles_required("admin")
def list_bookings():
    status = (request.args.get("status") or "").strip()
    q = (request.args.get("q") or "").strip()

    query = Booking.query
    if status:
        query = query.filter(Booking.status == status)
    if q:
        like = f"%{q}%"
        query = (
            query.join(User, Booking.user_id == User.id)
            .join(Trek, Booking.trek_id == Trek.id)
            .filter(
                User.name.ilike(like) | User.email.ilike(like) | Trek.name.ilike(like)
            )
        )
    bookings = query.order_by(Booking.id.desc()).all()
    return jsonify([booking_dict(b) for b in bookings])
