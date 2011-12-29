from base import *
from Session import Session
from Inspection import Inspection

"""
    The measurement object takes any regions of interest in an Inspection and
    returns a Result object with the appropriate measurement.
    
    The handler 
    
    Note that measurements are each linked to a single Inspection object.

    Measurement(dict( 
        name =  "largestblob",
        label = "Largest Blob",
        test_method = "largest_blob_area",
        parameters = dict( threshval = 127 ),
        result_labels = ["area","centroid"],
        is_numeric = 1,
        units =  "px",
        inspection_id = i._id))


"""
class Measurement(SimpleDoc): 
    name = mongoengine.StringField()
    #VALIDATION NEEDED: this should be a unique name
    label = mongoengine.StringField()
    test_method = mongoengine.StringField()
    parameters = mongoengine.DictField()
    result_labels = mongoengine.ListField(mongoengine.StringField())
    is_numeric = mongoengine.IntField()
    #VALIDATION NEEDED, data should be castable 
    units = mongoengine.StringField()
    inspection = mongoengine.ReferenceField(Inspection)

    def calculate(self, sample):
        
        function_ref = getattr(self, self.test_method)
        
        result = function_ref(sample)
           
        return Result({
            "measurement_id": self._id,
            "data": result,
            "is_numeric": self.is_numeric})
        
        return data
        
    def mean_color(self, img):
        return [str(c) for c in img.meanColor()]

    def largest_blob_area(self, img):
        parameters = self.parameters
        blobs = img.findBlobs(**parameters)
        
        if blobs:
            blobs[-1].draw()
            return [str(blobs[-1].area())]
        
        return ['']
    
    def count_blobs_hue(self, img):
        parameters = self.parameters
        huedistance = img.hueDistance(parameters['color']).invert()
        blobs = huedistance.findBlobs(int(parameters['threshold']))
        if not blobs:
            return ['']
        
        for b in blobs:
            b.image = img
            b.draw(Color.GREEN)
        return [len(blobs)]
            
from Result import Result
