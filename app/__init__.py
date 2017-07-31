from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
import os


from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.url_map.strict_slashes = False
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from app.auth import authenticate_blueprint
    app.register_blueprint(authenticate_blueprint)
    return app

app = create_app(os.getenv('APP_SETTINGS'))
