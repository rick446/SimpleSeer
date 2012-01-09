import sys, time, os, collections
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

import cherrypy
import urllib
try:
  import Image as pil
except(ImportError):
  import PIL.Image as pil

import cv
import IPython.Shell
try:
    import pyfirmata
except:
    print "Warning: Pyfirmata is not installed on this system, it is not required but recommended"
import redis
import mongoengine
import bson
import jsonpickle

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


try:
    import ujson
    jsonpickle.load_backend("ujson", "dumps", "loads", ValueError)
    jsonpickle.set_preferred_backend("ujson")

except ImportError:
    import json


#little wrapper functions to set defaults for dumps/loads behavior
def jsonencode(obj):
    return jsonpickle.encode(obj)

def jsondecode(data):
    return json.loads(data)
        
class SimpleDoc(mongoengine.Document):
    """
    All Seer objects should extend SimpleDoc, which wraps mongoengine.Document
    """
    _jsonignore = [None]
    
    
    def __getstate__(self):  
        ret = {}
        ret["id"] = self._data[None]
        for k in self._data.keys():
            if not k:
                continue
              
            v = self._data[k]
            if k[0] == "_" or k in self._jsonignore:
                continue
            if (hasattr(v, "__json__")):
                ret[k] = v.__json__()
            elif isinstance(v, SimpleCV.Image):
                ret[k] = v.applyLayers().getBitmap().tostring().encode("base64")
            elif isinstance(v, datetime):
                ret[k] = int(time.mktime(v.timetuple()) + v.microsecond/1e6)
            else:
                ret[k] = v
            
        return ret 
        
class SimpleEmbeddedDoc(mongoengine.EmbeddedDocument):
    """
    Any embedded docs (for object trees) should extend SimpleEmbeddedDoc
    """
    _jsonignore = [None]
    
    
    
class BSONObjectIDHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data['id'] = str(obj)
        return data
    
jsonpickle.handlers.Registry().register(bson.objectid.ObjectId, BSONObjectIDHandler)   

import SimpleCV
#from SimpleCV.Shell import *
from SimpleCV import Image, JpegStreamer, Camera, Color, cv, VirtualCamera
#from SimpleCV.Display import Display
