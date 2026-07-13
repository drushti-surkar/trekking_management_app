"""Programmatically create the database, seed roles, and the single Admin user.

Run once:  python create_admin.py
(Manual DB creation via DB Browser etc. is NOT allowed by the spec.)
"""
from flask_security import hash_password

from app import app
from extensions import db

ADMIN_EMAIL = "admin@tma.com"
ADMIN_PASSWORD = "admin123"


def seed():
    with app.app_context():
        db.create_all()
        ds = app.user_datastore

        # Roles
        for role in ("admin", "staff", "trekker"):
            ds.find_or_create_role(name=role)
        db.session.commit()

        # Single pre-existing Admin superuser
        if not ds.find_user(email=ADMIN_EMAIL):
            ds.create_user(
                email=ADMIN_EMAIL,
                username="admin",
                name="Administrator",
                password=hash_password(ADMIN_PASSWORD),
                roles=["admin"],
            )
            db.session.commit()
            print(f"Admin created -> {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        else:
            print("Admin already exists, skipping.")


if __name__ == "__main__":
    seed()
