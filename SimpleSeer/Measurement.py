from base import *
from Session import Session
from Result import Result

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
class Measurement(ming.Document):
    class __mongometa__:
        session = Session().mingsession
        name = 'measurement'
        
    _id = ming.Field(ming.schema.ObjectId)  
    name = ming.Field(str)
    #VALIDATION NEEDED: this should be a unique name
    label = ming.Field(str)
    test_method = ming.Field(str)
    parameters = ming.Field({str: None})
    result_labels = ming.Field(ming.schema.Array(str))
    
    is_numeric = ming.Field(int)
    #VALIDATION NEEDED, data should be castable 
    units = ming.Field(str)
    
    inspection_id = ming.Field(ming.schema.ObjectId)

    def calculate(self, sample):
        
        function_ref = getattr(self, self.test_method)
        
        result = function_ref(sample)
           
        return Result({
            "measurement_id": self._id,
            "data": result,
            "is_numeric": self.is_numeric})
        
        return data
        
    def save(self):
        self.m.save()
        
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
            
