from flask import Blueprint


# creates authentication blue print.
authenticate_blueprint = Blueprint("auth", __name__)

from . import views
