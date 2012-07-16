import sys, time, os, collections, re, warnings
from copy import copy, deepcopy
from datetime import datetime
import threading
import json
import pickle
import pygame.image
import numpy
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
from jsonpickle.pickler import Pickler
import logging


#little wrapper functions to set defaults for dumps/loads behavior
def jsonencode(obj):
#    import pdb; pdb.set_trace()
    return jsonpickle.encode(obj, unpicklable=False)

def jsondecode(data):
    return json.loads(data)
        
   


try:
    import ujson
    jsonpickle.load_backend("ujson", "dumps", "loads", ValueError)
    jsonpickle.set_preferred_backend("ujson")

except ImportError:
    import json


#note these handlers are not ok for "picklable" stuff
class BSONObjectIDHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data={}):
        return str(obj)

    
class MongoEngineFileFieldHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data={}):
        if not obj.grid_id:
            return None
        
        return "/gridfs/" + str(obj.grid_id)

class MongoEngineBaseListHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data={}):
        return mebaselist_handle(obj)
    
def mebaselist_handle(obj):
        ret = []
        j = Pickler(True, 100)
        return [j.flatten(i) for i in obj]
        
class MongoEngineBaseDictHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return mebasedict_handle(obj)
        
def mebasedict_handle(obj):
    data = {}
    j = Pickler(True, 100)

    for k in obj.keys():
        data[k] = j.flatten(obj[k])
    return data
    
class NumpyIntHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return int(obj)
    
class FrameFeatureHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data = {}):
        j = Pickler(True, 100)

        for k in obj.__getstate__().keys():
            data[k] = j.flatten(obj[k])
        return data
    
jsonpickle.handlers.Registry().register(bson.objectid.ObjectId, BSONObjectIDHandler)   
jsonpickle.handlers.Registry().register(mongoengine.base.BaseList, MongoEngineBaseListHandler)
jsonpickle.handlers.Registry().register(mongoengine.base.BaseDict, MongoEngineBaseDictHandler)
jsonpickle.handlers.Registry().register(mongoengine.fields.GridFSProxy, MongoEngineFileFieldHandler)
jsonpickle.handlers.Registry().register(numpy.int64, NumpyIntHandler)



import SimpleCV
#from SimpleCV.Shell import *
from SimpleCV import Image, JpegStreamer, Camera, Color, cv, VirtualCamera, Kinect
#from SimpleCV.Display import Display
