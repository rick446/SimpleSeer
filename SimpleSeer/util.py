import time
import collections
from functools import wraps

from flask import make_response

from base import jsonencode
import mongoengine

class LazyProperty(object):

    def __init__(self, func):
        self._func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, klass=None):
        if obj is None: return None
        result = obj.__dict__[self.__name__] = self._func(obj)
        return result

class Clock(object):
    '''Simple class that allows framerate control'''

    def __init__(self, rate_in_hz, sleep=None):
        if sleep is None: sleep = time.sleep
        self.period = 1.0 / rate_in_hz
        self.ts = time.time()
        self.sleep = sleep

    def tick(self):
        '''Call at the top of your timed loop to wait until the clock
        ticks. If a negative wait is called for, don't wait at all.
        '''
        now = time.time()
        remaining = self.ts - now
        if remaining > 0:
            self.sleep(remaining)
            self.ts = self.ts + self.period
        else:
            self.ts = now + self.period

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
    if SS().disabled:  #check to see if we have seer
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
