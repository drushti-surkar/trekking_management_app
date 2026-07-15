from datetime import datetime

from flask_security.models import fsqla_v3 as fsqla

from extensions import db

fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    name = db.Column(db.String(120))

    staff_profile = db.relationship(
        "StaffProfile", back_populates="user", uselist=False,
        cascade="all, delete-orphan",
    )
    
    assigned_treks = db.relationship(
        "Trek", back_populates="assigned_staff",
        foreign_keys="Trek.assigned_staff_id",
    )
    bookings = db.relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan",
    )


class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    contact_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Active")

    user = db.relationship("User", back_populates="staff_profile")


class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    status = db.Column(db.String(20), default="Pending", nullable=False)

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_staff = db.relationship(
        "User", back_populates="assigned_treks", foreign_keys=[assigned_staff_id],
    )
    bookings = db.relationship(
        "Booking", back_populates="trek", cascade="all, delete-orphan",
    )


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked", nullable=False)
    payment_status = db.Column(db.String(20), default="Pending")

    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")

    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek"),
    )
