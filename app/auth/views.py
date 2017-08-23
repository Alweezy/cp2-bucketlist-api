from flask.views import MethodView
from flask import jsonify, request, make_response

import re


from . import authenticate_blueprint
from app.models import User

EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class SignUpView(MethodView):
    """Models signing up as a new user."""

    def post(self):
        """for requests of kind post from /auth/register/"""
        if request.data["username"].strip() and request.data["password"].strip():
            user = User.query.filter_by(
                username=request.data["username"]).first()
            if user:
                # if user exists, ask them to log in.
                res = {
                    "message": "User already exists. Please login"
                }

                return make_response(jsonify(res)), 409

            else:
                try:
                    data = request.data

                    username = data["username"]
                    password = data["password"]
                    email = data["email"]
                    if email and EMAIL_REGEX.match(email):
                        user = User(username=username, password=password,
                                    email=email)
                        user.save()

                        response = {
                            "message": 'User registration successful.'
                        }

                        return make_response(jsonify(response)), 201
                    else:
                        response = {
                            "message": 'Cannot register with invalid email.'
                        }

                        return make_response(jsonify(response)), 400

                except Exception as e:
                    response = {
                        "message": str(e)
                    }

                    return make_response(jsonify(response)), 401

        else:
            response = {
                "message": "Error. The username or password cannot be empty"
            }
            return make_response(jsonify(response)), 400


class SignInView(MethodView):
    """Models signing in as a registered user"""

    def post(self):
        """for requests of kind post from /auth/login/"""
        try:
            if request.data["username"].strip() and request.data["password"].strip():
                user = User.query.filter_by(
                    username=request.data["username"]).first()
                # Authenticate the user using the password
                if user and user.verify_password(request.data["password"]):
                    # Generate the access token which will be used
                    # as the authorization header
                    token = user.generate_auth_token(user.id)
                    if token:
                        response = {
                            "message": "You logged in successfully.",
                            "token": token.decode()
                        }

                        return make_response(jsonify(response)), 200

                elif not user:
                    # If the user does not exists
                    response = {
                        "message": "Invalid email or password. "
                                   "Please try again."
                    }

                    return make_response(jsonify(response)), 401
            else:
                # Either username or password is not provided
                response = {
                    "message": "Error. The username or password "
                               "cannot be empty"
                }

                return make_response(jsonify(response)), 400

        except Exception as e:
            response = {
                "message": str(e)
            }

            # Return 500(Internal Server Error)
            return make_response(jsonify(response)), 500


# the API resources definition
registration_view = SignUpView.as_view("register_view")
login_view = SignInView.as_view("login_view")

#  sign up  URL /auth/register/  rule definition and blue print
authenticate_blueprint.add_url_rule("/auth/register/", view_func=registration_view,
                                    methods=["POST"])

# sign up  URL /auth/login/  rule definition and addition to blue print
authenticate_blueprint.add_url_rule("/auth/login/", view_func=login_view,
                                    methods=["POST"])




