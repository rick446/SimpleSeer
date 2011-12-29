from base import *
from Session import *


class FrameFeature(mongoengine.EmbeddedDocument):
   
    featuretype = mongoengine.StringField()
    featuredata = mongoengine.DictField()  #this holds any type-specific feature data
    featurepickle = mongoengine.StringField() #a pickle of the feature, for rendering out
    _featurecache = ''
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

        self.x = data.x
        self.y = data.y
        self.points = deepcopy(data.points)
        self.area = data.area()
        self.width = data.width()
        self.height = data.height()
        self.angle = data.angle()
        #self.meancolor = data.meanColor()
        self.featuretype = data.__class__.__name__
        
        for k in data.__dict__:
            if self.featuredata_mask.has_key(k) or hasattr(self, k):
                continue
            value = getattr(data, k)
            #here we need to handle all the cases for odd bits of data, but
            #for now we'll just toss them
            if type(value) == cv.iplimage:
                self.featuredata[k] = Image(value)
            else:
                self.featuredata[k] = str(value)
    @property
    def feature(self):
        return pickle.loads(self.featurepickle)
    

    def __json__(self):
        data = deepcopy(self._data)
        del data['featurepickle']
        #do something with image refs
        return SimpleDocJSONEncoder().encode(data)

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
        
#we can't make a recursive object since the class isn't yet declared    

    
