"""Shared extension singletons, initialized in app.py."""
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security

db = SQLAlchemy()
security = Security()
