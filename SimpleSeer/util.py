from functools import wraps

from flask import make_response

from base import jsonencode

def jsonify(f):
    """
    We're going to use our own jsonify decorator, which uses our jsonencode function
    which routes thru json-pickle
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        obj = f(*args, **kwargs)
        if obj is None:
            obj = {}
            
        resp = make_response(jsonencode(obj), 200)
        resp.headers["Content-Type"] = 'application/json'
        return resp
    return decorated_function


