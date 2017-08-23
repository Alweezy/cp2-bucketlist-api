import os
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    """creates an app instance
    :param config_name: The name of the confiuration;
    whether development, staging or production.
    :return: app
    """
    app = FlaskAPI(__name__, instance_relative_config=True)
    CORS(app)
    app.url_map.strict_slashes = False
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from app.auth import authenticate_blueprint
    app.register_blueprint(authenticate_blueprint)
    return app

app = create_app(os.getenv('APP_SETTINGS'))
