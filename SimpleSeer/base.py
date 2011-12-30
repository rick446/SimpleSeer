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



class SimpleDocJSONEncoder(json.JSONEncoder):
    def default(self, obj, **kwargs):
        
        if (hasattr(obj, "__json__")):
            return json.loads(obj.__json__()) #TODO that's a bit crap
            
        if isinstance(obj, SimpleCV.Image):
            return obj.applyLayers().getBitmap().tostring().encode("base64")
        
        if isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
            
        if isinstance(obj, datetime):
            return int(time.mktime(obj.timetuple()) + obj.microsecond/1e6)
        else:            
            return json.JSONEncoder.default(obj, **kwargs)

class SimpleDoc(mongoengine.Document):
    """
    All Seer objects should extend SimpleDoc, which wraps mongoengine.Document
    """
    _jsonignore = [None]
        
    def __json__(self):
        data = deepcopy(self._data)
        
        data["id"] = str(self.id)
        for ignore in self._jsonignore:
            del data[ignore]
        
        #remove private data
        for k in [k for k in data.keys() if k[0] == "_"]:
          del data[k]
        
        
        return SimpleDocJSONEncoder().encode(data)
        
            

import SimpleCV
#from SimpleCV.Shell import *
from SimpleCV import Image, JpegStreamer, Camera, Color, cv
#from SimpleCV.Display import Display
