import os

basedir = os.path.abspath(os.path.dirname(__file__))


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

    # Celery + Redis
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    # Redis cache (separate db from the Celery broker)
    CACHE_REDIS_URL = "redis://localhost:6379/1"
    CACHE_TTL = 60  # seconds

    # Email — local SMTP (Mailhog: SMTP 1025, web UI 8025)
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_SENDER = "no-reply@tma.local"
    ADMIN_EMAIL = "admin@manzil.com"

    # CSV export output directory
    EXPORT_DIR = os.path.join(basedir, "exports")
