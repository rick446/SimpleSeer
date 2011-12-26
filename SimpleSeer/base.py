import sys, time, os
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


class SimpleDoc(mongoengine.Document):
    """
    All Seer objects should extend SimpleDoc, which wraps mongoengine.Document
    """
    #@classmethod
    #def find(cls, *args, **kwargs):
    #    return cls.m.find(*args, **kwargs)
    
    #@classmethod
    #def remove(cls, *args, **kwargs):
    #    return cls.m.remove(*args, **kwargs)
    
    #def save(self):
    #    self.m.save()
        
    #def __json__(self):
        





import SimpleCV
#from SimpleCV.Shell import *
from SimpleCV import Image, JpegStreamer, Camera, Color, cv
#from SimpleCV.Display import Display
