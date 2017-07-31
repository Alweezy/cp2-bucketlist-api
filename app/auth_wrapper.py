from functools import wraps

from flask import jsonify, request, make_response

from app.models import User


def evaluate_auth(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        header = request.headers.get("Authorization")
        if header:
            token = header
            # extract user_id from token
            user_id = User.verify_token(token)
            if not isinstance(user_id, str):
                return function(user_id=user_id, *args, **kwargs)
            else:
                response = jsonify({
                    "message": user_id
                })
                response.status_code = 401
                return response

        else:
            # if token is missing
            response = {
                "message": "Register or log in to access this resource"
            }
            return make_response(jsonify(response)), 401

    return decorator
