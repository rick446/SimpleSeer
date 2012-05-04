import sys, time, os, collections, re, warnings
from copy import copy, deepcopy
from datetime import datetime
import threading
import json
import pickle
import pygame.image
from multiprocessing import Process, Queue, Pipe
import threading
import logging
from StringIO import StringIO
import types
import atexit

#~ import cherrypy
import urllib
try:
    import Image as pil
except(ImportError):
    import PIL.Image as pil

import cv

try:
    import pyfirmata
except:
    warnings.warn(
        'Pyfirmata is not installed on this system. '
        'It is not required but recommended', Warning)

#import redis
import mongoengine
import bson
import jsonpickle
import logging




try:
    import ujson
    jsonpickle.load_backend("ujson", "dumps", "loads", ValueError)
    jsonpickle.set_preferred_backend("ujson")

except ImportError:
    import json


#little wrapper functions to set defaults for dumps/loads behavior
def jsonencode(obj):
    return jsonpickle.encode(obj, unpicklable=False)

def jsondecode(data):
    return json.loads(data)
        
   
#note these handlers are not ok for "picklable" stuff
class BSONObjectIDHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return str(obj)
    
class MongoEngineFileFieldHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        if not obj.grid_id:
            return None
        
        return "/gridfs/" + str(obj.grid_id)
        
class MongoEngineBaseListHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        #data["values"] = list(obj)
        ret = []
        for i in obj:
            if hasattr(i, "__getstate__"):
                ret.append(i.__getstate__())
            else:
                ret.append(i)
        return ret

class MongoEngineBaseDictHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data.update(obj)
        return data
    
    
jsonpickle.handlers.Registry().register(bson.objectid.ObjectId, BSONObjectIDHandler)   
jsonpickle.handlers.Registry().register(mongoengine.base.BaseList, MongoEngineBaseListHandler)
jsonpickle.handlers.Registry().register(mongoengine.base.BaseDict, MongoEngineBaseDictHandler)
jsonpickle.handlers.Registry().register(mongoengine.fields.GridFSProxy, MongoEngineFileFieldHandler)



import SimpleCV
#from SimpleCV.Shell import *
from SimpleCV import Image, JpegStreamer, Camera, Color, cv, VirtualCamera, Kinect
#from SimpleCV.Display import Display
