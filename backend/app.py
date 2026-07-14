import os


from flask import Flask, render_template
from flask_security import SQLAlchemyUserDatastore

from config import Config
from extensions import db, security
import models

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")

INSTANCE_DIR = os.path.join(BACKEND_DIR, "instance")


def create_app(config_class=Config):
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    app = Flask(
        __name__,
        instance_path=INSTANCE_DIR,
        template_folder=FRONTEND_DIR,
        static_folder=FRONTEND_DIR,
        static_url_path="/static",
    )
    app.config.from_object(config_class)

    db.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)

    security.init_app(app, user_datastore)

    app.user_datastore = user_datastore


    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.trekker import trekker_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(trekker_bp)


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
