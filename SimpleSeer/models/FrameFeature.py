import cPickle as pickle
from copy import deepcopy

import cv
import numpy as np
import mongoengine
import mongoengine.base

import SimpleCV

from .base import SimpleEmbeddedDoc
from SimpleSeer.base import mebasedict_handle, mebaselist_handle



#helper function to get difficult to encode types out of SimpleCV native types
def scv_cleanse(value):
    if type(value) == cv.iplimage or isinstance(value, SimpleCV.Image):
        return
    if type(value) == list or type(value) == tuple:
        return [scv_cleanse(v) for v in value]
    if type(value) == dict:
        d = {}
        for k in value.keys():
            d[k] = scv_cleanse(value[k])
        return d
    if issubclass(type(value), np.integer):
        return int(value)
    if issubclass(type(value), np.float):
        return float(value)
    else:
        return value




class FrameFeature(SimpleEmbeddedDoc, mongoengine.EmbeddedDocument):
   
    featuretype = mongoengine.StringField()
    featuredata = mongoengine.DictField()  #this holds any type-specific feature data
    featurepickle = mongoengine.BinaryField() #a pickle of the feature, for rendering out
    _featurebuffer = ''
    #this is incredibly sloppy, really -- but we're going to get away with it
    #because features are essentially immutable
    
    inspection = mongoengine.ObjectIdField()
    children = mongoengine.ListField(mongoengine.GenericEmbeddedDocumentField())


    
    #feature attributes need to be in this list to be queryable
    #note that plugins can inject into this
    points = mongoengine.ListField()
    x = mongoengine.FloatField()
    y = mongoengine.FloatField()
    area = mongoengine.FloatField()
    width = mongoengine.FloatField()
    height = mongoengine.FloatField()
    angle = mongoengine.FloatField()
    meancolor = mongoengine.ListField(mongoengine.FloatField())
    
    #these are feature properties which are not saved
    #note that plugins can inject into this
    featuredata_mask = {
        "image": False
    }
    
    #this converts a SimpleCV Feature object into a FrameFeature
    #clean this up a bit
    def setFeature(self, data):
        self._featurecache = data
        imgref = data.image
        data.image = ''  #remove image ref for pickling
        self.featurepickle = pickle.dumps(data)
        data.image = imgref

        self.x = int(data.x)
        self.y = int(data.y)
        self.points = scv_cleanse(deepcopy(data.points))
        self.area = scv_cleanse(data.area())
        self.width = scv_cleanse(data.width())
        self.height = scv_cleanse(data.height())
        self.angle = scv_cleanse(data.angle())
        self.meancolor = scv_cleanse(data.meanColor())
        self.featuretype = data.__class__.__name__
        
        datadict = {}
        if hasattr(data, "__getstate__"):
            datadict = data.__getstate__()
        else:
            datadict = data.__dict__
            
        for k in datadict:
            if self.featuredata_mask.has_key(k) or hasattr(self, k) or k[0] == "_":
                continue
            value = getattr(data, k)
            #here we need to handle all the cases for odd bits of data, but
            #for now we'll just toss them
            self.featuredata[k] = scv_cleanse(value)
            
    @property
    def feature(self):
        if not self._featurebuffer:
            self._featurebuffer = pickle.loads(self.featurepickle)
        return self._featurebuffer
    

    def __getstate__(self):
        ret = {}
        skipfields = ["featurepickle", "children"]
        
        #handle all the normal fields
        for k in self._data.keys():
            if k in skipfields:
                continue
            
            v = self._data[k]
            if k == "inspection":
                ret[k] = str(v)
        
        #handle all children
        ret["children"] = [c.__getstate__() for c in self.children]
        return ret

    #cribbed from http://www.ariel.com.au/a/python-point-int-poly.html
    #should be moved to SimpleCV/Features
    def contains(self, point):
        x, y  = point
        poly = self.points
        n = len(poly)
        inside = False
        if n < 3:
            return False
    
        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside  
