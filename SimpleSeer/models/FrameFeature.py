import cPickle as pickle
from cStringIO import StringIO
from binascii import b2a_base64, a2b_base64
from copy import deepcopy

import cv
import numpy as np
import mongoengine
import mongoengine.base

import SimpleCV

from .base import SimpleEmbeddedDoc, SONScrub
from SimpleSeer.base import mebasedict_handle, mebaselist_handle

def _numpy_save(son, collection):
    sio = StringIO()
    np.save(sio, son)
    return sio.getvalue()

def _numpy_load(son, collection):
    sio = StringIO(son)
    return np.load(sio)

SONScrub.scrub_type(cv.iplimage)
SONScrub.scrub_type(SimpleCV.Image)
SONScrub.register_bsonifier(np.integer, lambda v,c: int(v))
SONScrub.register_bsonifier(np.float, lambda v,c: float(v))
SONScrub.register_bsonifier(np.float64, lambda v,c: float(v))
SONScrub.register_bintype(np.ndarray, _numpy_save, _numpy_load)
# matrices are instances of np.ndarray, no need to register them again
# SONScrub.register_bintype(np.matrix, _numpy_save, _numpy_load)

class FrameFeature(SimpleEmbeddedDoc, mongoengine.EmbeddedDocument):

    featuretype = mongoengine.StringField()
    featuredata = mongoengine.DictField()  #this holds any type-specific feature data
    # featurepickle = mongoengine.BinaryField() #a pickle of the feature, for
    # rendering out
    featurepickle_b64 = mongoengine.StringField() #a pickle of the feature, for rendering out
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
    featuredata_mask = set(['image'])
    
    cleanse_mask = set([
        'mContour', 'mContourAppx', 'mConvexHull', 'mHoleContour',
        'mVertEdgeHist'])

    @property
    def featurepickle(self):
        return a2b_base64(self.featurepickle_b64)
    
    @featurepickle.setter
    def featurepickle(self, value):
        self.featurepickle_b64 = b2a_base64(value)
    
    #this converts a SimpleCV Feature object into a FrameFeature
    #clean this up a bit
    def setFeature(self, data):
    
        self._featurecache = data
        self.x = int(data.x)
        self.y = int(data.y)
        self.points = deepcopy(data.points)

        self.area = data.area()
        self.width = data.width()
        self.height = data.height()
        self.angle = data.angle()

        self.meancolor = data.meanColor()
        self.featuretype = data.__class__.__name__
        
        data.image = ''
        self.featurepickle = pickle.dumps(data)

        

        datadict = {}
        if hasattr(data, "__getstate__"):
            datadict = data.__getstate__()
        else:
            datakeys = [k for k in dir(data) if not (str(type(getattr(data,k))) == "<type 'instancemethod'>" or k.startswith("_")) ]
            for k in datakeys:
                datadict[k] = getattr(data, k)
                        
        for k in datadict:
            if k in self.featuredata_mask or hasattr(self, k) or k[0] == "_":
                continue
                            
            value = getattr(data, k)
            if k in self.cleanse_mask:
                self.featuredata[k] = value
                continue
            
            #here we need to handle all the cases for odd bits of data
            self.featuredata[k] = value
            
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
            
            ret[k] = self._data[k]
            if k == "inspection":
                ret[k] = str(self._data[k])
        
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
