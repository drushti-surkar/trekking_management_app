"""Flask application factory for the Trekking Management Application."""
from flask import Flask, render_template
from flask_security import SQLAlchemyUserDatastore

from config import Config
from extensions import db, security
import models


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security.init_app(app, user_datastore)
    # Keep the datastore handy for scripts / API resources
    app.user_datastore = user_datastore

    # API blueprints
    from api.auth import auth_bp
    from api.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # Single Jinja2 entry point for the Vue (CDN) SPA
    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Port 5001: macOS uses 5000 for AirPlay Receiver
    app.run(debug=True, port=5001)
