import collections
from functools import wraps

from flask import make_response
from decorator import decorator

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


#cribbed from
#http://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str
def utf8convert(data):
    if isinstance(data, unicode):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(utf8convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(utf8convert, data))
    else:
        return data

def _memoize(func, *args, **kw):
    if kw: # frozenset is used to ensure hashability
        key = args, frozenset(kw.iteritems())
    else:
        key = args
    cache = func.cache # attribute added by memoize
    try:
        return cache[key]
    except KeyError:
        pass
    cache[key] = result = func(*args, **kw)
    return result

def memoize(f):
    f.cache = {}
    return decorator(_memoize, f)

@memoize
def get_seer():
    from SimpleSeer import SimpleSeer
    return SimpleSeer()
