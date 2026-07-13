"""Application configuration."""


class Config:
    # Core Flask
    SECRET_KEY = "tma-dev-secret-change-in-prod"

    # Database (SQLite, created programmatically)
    SQLALCHEMY_DATABASE_URI = "sqlite:///tma.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security-Too
    SECURITY_PASSWORD_SALT = "tma-password-salt-change-in-prod"
    SECURITY_PASSWORD_HASH = "bcrypt"
    # Token-based auth for the Vue SPA (no server-rendered forms / no CSRF on API)
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    WTF_CSRF_ENABLED = False
    SECURITY_CSRF_PROTECT_MECHANISMS = []
    # Trekkers self-register; Admin/Staff are created, so registration stays enabled
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CONFIRMABLE = False
    # API-only: never redirect unauthenticated requests to an HTML login view
    SECURITY_UNAUTHORIZED_VIEW = None
