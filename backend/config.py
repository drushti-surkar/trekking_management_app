import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "tma-dev-secret-change-in-prod"

    SQLALCHEMY_DATABASE_URI = "sqlite:///tma.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECURITY_PASSWORD_SALT = "tma-password-salt-change-in-prod"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    WTF_CSRF_ENABLED = False
    SECURITY_CSRF_PROTECT_MECHANISMS = []
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CONFIRMABLE = False
    SECURITY_UNAUTHORIZED_VIEW = None

    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    CACHE_REDIS_URL = "redis://localhost:6379/1"
    CACHE_TTL = 60

    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_SENDER = "no-reply@tma.local"
    ADMIN_EMAIL = "admin@manzil.com"
    ADMIN_PASSWORD = "admin123"

    EXPORT_DIR = os.path.join(basedir, "exports")
