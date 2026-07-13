"""Database models for the Trekking Management Application.

Roles: admin / staff / trekker (single role per user).
Core tables: User, Role, StaffProfile, Trek, Booking.
"""
from datetime import datetime

from flask_security.models import fsqla_v3 as fsqla

from extensions import db

# Wire Flask-Security's standard mixins to our db so User/Role get the
# required fields (fs_uniquifier, active, password, roles link table, etc.)
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    """admin / staff / trekker."""
    pass


class User(db.Model, fsqla.FsUserMixin):
    """Unified user model for all three roles."""
    name = db.Column(db.String(120))

    # One-to-one staff details (only populated for staff users)
    staff_profile = db.relationship(
        "StaffProfile", back_populates="user", uselist=False,
        cascade="all, delete-orphan",
    )
    # Treks this user manages (only for staff)
    assigned_treks = db.relationship(
        "Trek", back_populates="assigned_staff",
        foreign_keys="Trek.assigned_staff_id",
    )
    # Bookings this user made (only for trekkers)
    bookings = db.relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan",
    )


class StaffProfile(db.Model):
    """Extra details for a Trek Staff member (one-to-one with User)."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    contact_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Active")  # Active / Inactive

    user = db.relationship("User", back_populates="staff_profile")


class Trek(db.Model):
    """A trekking event created and managed in the system."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)   # Easy / Moderate / Hard
    duration_days = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    # Pending / Approved / Open / Closed / Completed
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
    """A record of a user booking a trek."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked", nullable=False)   # Booked / Cancelled / Completed
    payment_status = db.Column(db.String(20), default="Pending")          # Pending / Paid

    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")

    # A user cannot book the same trek twice
    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek"),
    )
