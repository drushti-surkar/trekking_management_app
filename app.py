"""Flask application factory for the Trekking Management Application."""
from flask import Flask
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

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
