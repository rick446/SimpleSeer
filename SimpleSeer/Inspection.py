from base import *
from Session import *
from FrameFeature import FrameFeature


class Region(SimpleCV.Feature):
    
    def __init__(self, startx, starty, width, height):
        
        point = (startx, starty)
        self.x = point[0] + width / 2
        self.y = point[1] + height / 2
        self.points = [tuple(point),
            (point[0] + width, point[1]),
            (point[0] + width, point[1] + height),
            (point[0], point[1] + height)]

class Inspection(SimpleDoc):
    """
    
    An Inspection determines what part of an image to look at from a given camera
    and what Measurement objects get taken.  It has a single handler, the method,
    which determines ROI for the measurements.
    
    The method determines if measurements are or are not taken.  A completely
    passive method would return the entire image space (taking measurements
    on every frame), and an "enabled = 0" equivalent would be method always
    returning None.
    
    The method can return several samples, pieces of the evaluated frame,
    and these get passed in turn to each Measurement.
    
    The results from these measurements are aggregated and returned from the
    Inspection.execute() function, which gives all samples to each measurement.
    
    insp = Inspection(
        name = "Area of Interest",
        method = "region",
        camera = "Default Camera",
        parameters = dict( x =  100, y = 100, w = 400, h = 300)) #x,y,w,h

    insp.save()
    
    Measurement(..., inspection_id = insp.id )
    
    results = insp.execute()
    
    """
    name = mongoengine.StringField()
    parent = mongoengine.ObjectIdField()
    
    method = mongoengine.StringField()
    #TODO, validate that this method exists
    camera = mongoengine.StringField()
    #TODO validate that this camera exists
    parameters = mongoengine.DictField()
    #TODO validate against function
    filters = mongoengine.DictField()
    #TODO validate against valid fields for the feature type
    richattributes = mongoengine.DictField()
    #TODO validate against attributes
    morphs = mongoengine.ListField()
    #list of dicts for morph operations
    #TODO validate agains morph operations
    
                                           
    def execute(self, image, parents = {}):
        """
        The execute method takes in a frame object, executes the method
        and sends the samples to each measurement object.  The results are returned
        as a multidimensional array [ samples ][ measurements ] = result
        """
        
        #execute the morphs?
        
        #recursion stopper so we don't accidentally end up in any loops
        if parents.has_key(self.id):
            return []
        
        method_ref = getattr(self, self.method)
        #get the ROI function that we want
        #note that we should validate/roi method
 
        results = method_ref(image)
        
        if not results:
            return []
        
        for r in results:
            r.inspection = self.id
        
        
        children = self.children
        
        if not children:
            return results
        
        if children:
            newparents = deepcopy(parents)
            newparents[self.id] = True
            for r in results:
                f = r.feature
                f.image = image
                roi = f.crop()
            
                for child in children:    
                    r.children.extend(child.execute(roi, newparents))
                
        
        return results
    
    @property
    def children(self):
        return Inspection.objects(parent = self.id)
        
    @classmethod    
    def inspect(self):
        return SimpleSeer.SimpleSeer().inspect()

    #below are "core" inspection functions
    def region(self, image):        
        params = utf8convert(self.parameters)
        
        if params['x'] + params['w'] > image.width or params['y'] + params['h'] > image.height:
            return []
        
        ff = FrameFeature()
        ff.setFeature(Region(params['x'], params['y'], params['w'], params['h']))
        return [ff]
        
    def blob(self, image):
        params = utf8convert(self.parameters)
        
        
        #if we have a color parameter, lets threshold        
        blobs = image.findBlobs(**params)
        if not blobs:
            return []
        
        feats = []
        for b in blobs:
            ff = FrameFeature()
            ff.setFeature(b)
            feats.append(ff)
            
        return feats

from Measurement import Measurement
import SimpleSeer
