from flask import request, jsonify
from functools import wraps
from flask_jwt_extended import get_jwt_identity


def rbac_auth(permissions=["user", "admin"]):
    def _wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            if not current_user["role"] in permissions:
                return jsonify({"code": 401, "message": "User doesn't posses enough permissions"}), 401
            result = func(*args, **kwargs)
            return result
        return wrapper
    return _wrapper
