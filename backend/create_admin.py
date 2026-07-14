from flask_security import hash_password

from app import app
from extensions import db

ADMIN_EMAIL = "admin@manzil.com"
ADMIN_PASSWORD = "admin123"


def seed():
    with app.app_context():
        db.create_all()
        ds = app.user_datastore

        # Roles
        for role in ("admin", "staff", "trekker"):
            ds.find_or_create_role(name=role)
        db.session.commit()

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
