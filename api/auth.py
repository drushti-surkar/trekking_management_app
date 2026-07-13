"""Authentication API: register (trekkers only), login, logout, current user.

Uses Flask-Security-Too's datastore + password hashing + token auth.
Admin and Staff are created elsewhere (script / admin dashboard); this
`/register` endpoint always creates a plain Trekker.
"""
import re

from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from flask_security.utils import hash_password, verify_password

from extensions import db, security

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _role_name(user):
    return user.roles[0].name if user.roles else None


def _user_payload(user):
    return {
        "token": user.get_auth_token(),
        "role": _role_name(user),
        "name": user.name,
        "email": user.email,
    }


@auth_bp.post("/register")
def register():
    """Trekker self-registration."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # Backend validation
    if not name or not email or not password:
        return jsonify(error="Name, email and password are required."), 400
    if not EMAIL_RE.match(email):
        return jsonify(error="Invalid email address."), 400
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters."), 400

    ds = security.datastore
    if ds.find_user(email=email):
        return jsonify(error="An account with this email already exists."), 409

    user = ds.create_user(
        email=email,
        name=name,
        password=hash_password(password),
        roles=["trekker"],
    )
    db.session.commit()
    return jsonify(_user_payload(user)), 201


@auth_bp.post("/login")
def login():
    """Login for any role; returns an auth token + role for redirect."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify(error="Email and password are required."), 400

    ds = security.datastore
    user = ds.find_user(email=email)
    if not user or not verify_password(password, user.password):
        return jsonify(error="Invalid email or password."), 401
    if not user.active:
        return jsonify(error="Your account has been deactivated. Contact the admin."), 403

    return jsonify(_user_payload(user)), 200


@auth_bp.post("/logout")
@auth_required("token")
def logout():
    """Invalidate the current token (rotates the token uniquifier)."""
    security.datastore.set_uniquifier(current_user)
    db.session.commit()
    return jsonify(message="Logged out."), 200


@auth_bp.get("/me")
@auth_required("token")
def me():
    """Return the current authenticated user (used to rehydrate the SPA)."""
    return jsonify(
        role=_role_name(current_user),
        name=current_user.name,
        email=current_user.email,
    ), 200
