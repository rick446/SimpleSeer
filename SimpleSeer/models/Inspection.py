from copy import deepcopy

import mongoengine
from formencode import validators as fev
from formencode import schema as fes
import formencode as fe


from SimpleSeer import validators as V
from SimpleSeer import util


from .base import SimpleDoc, WithPlugins
from .Measurement import Measurement
from .FrameFeature import FrameFeature

class InspectionSchema(fes.Schema):
    parent = V.ObjectId(if_empty=None, if_missing=None)
    name = fev.UnicodeString(not_empty=True)
    method = fev.UnicodeString(not_empty=True)
    camera = fev.UnicodeString(if_empty="")
    parameters = V.JSON(if_empty=dict, if_missing=None)
    filters = V.JSON(if_empty=dict, if_missing=None)
    richattributes = V.JSON(if_empty=dict, if_missing=None)
    morphs = fe.ForEach(fev.UnicodeString(), convert_to_list=True)


class Inspection(SimpleDoc, WithPlugins, mongoengine.Document):
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

    def __repr__(self):
      return "[%s Object <%s> ]" % (self.__class__.__name__, self.name)
                                           
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
        
        method_ref = self.get_plugin(self.method)
        #get the ROI function that we want
        #note that we should validate/roi method
 
        featureset = method_ref(image)
        
        if not featureset:
            return []
        
        #we're executing an unsaved inspection, which can have no children
        if not self.id:
            return featureset
        
        for r in featureset:
            r.inspection = self.id
        
        children = self.children
        
        if not children:
            return featureset
        
        if children:
            newparents = deepcopy(parents)
            newparents[self.id] = True
            for r in featureset:
                f = r.feature
                f.image = image
                roi = f.crop()
            
                for child in children:    
                    r.children.extend(child.execute(roi, newparents))
                
        
        return featureset
    
    @property
    def children(self):
        return Inspection.objects(parent = self.id)
        
    @property
    def measurements(self):
        return Measurement.objects(inspection = self.id)
        
    @classmethod    
    def inspect(self):
        import SimpleSeer
        return SimpleSeer.SimpleSeer().inspect()

    #overload the save function so that all inspections are reloaded if one is updated
    def save(self):
        ret = super(Inspection, self).save()
        util.get_seer().reloadInspections()
        return ret
    
    
    def face(self, image):
        params = util.utf8convert(self.parameters)
        
        faces = image.findHaarFeatures("/usr/local/share/opencv/haarcascades/haarcascade_frontalface_alt.xml")
        
        if not faces:
            return []
        
        features = []
        for f in faces:
            ff = FrameFeature()
            ff.setFeature(f)
            features.append(ff)
        
        return features
