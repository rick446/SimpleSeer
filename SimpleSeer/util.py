import collections
from functools import wraps

from flask import make_response
from decorator import decorator

from base import jsonencode
import mongoengine

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
#note this casts all iterables to lists
def utf8convert(data):
    if isinstance(data, basestring):
        return data.encode('utf-8')
    elif isinstance(data, collections.Mapping):
        return dict(map(utf8convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return list(map(utf8convert, data))
    else:
        return data

def get_seer():
    from .SimpleSeer import SimpleSeer as SS
    from . import service
    if SS is None:
        return service.SeerProxy2()
    return SS()

def initialize_slave():
	from .Session import Session
	from . import models as M
	#if we're in slave mode, rip thru the models and 
	#run a count() -- this gets over a bug in mongoengine
	#where the ensure_indexes fault on being against a slavedb
	if Session().mongo.has_key("is_slave") and Session().mongo["is_slave"]:
		for m in M.models:
			try:
				exec("M."+m+".objects.count()")
			except:
				pass
		mongoengine.connection._dbs["default"].slave_okay = True
