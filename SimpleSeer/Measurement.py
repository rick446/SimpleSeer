from base import *
from Session import Session
from Inspection import Inspection

"""
    The measurement object takes any regions of interest in an Inspection and
    returns a Result object with the appropriate measurement.
    
    The handler 
    
    Note that measurements are each linked to a single Inspection object.

    Measurement(name =  "blob_largest_area",
        label = "Blob Area",
        method = "area",
        parameters = dict(),
        featurecriteria = dict( index = -1 ),
        units =  "px",
        inspection = insp.id)


"""
class Measurement(SimpleDoc): 
    name = mongoengine.StringField()
    #VALIDATION NEEDED: this should be a unique name
    label = mongoengine.StringField()
    method = mongoengine.StringField()
    parameters = mongoengine.DictField()
    units = mongoengine.StringField()
    inspection = mongoengine.ObjectIdField()
    featurecriteria = mongoengine.DictField()

    def execute(self, frame, features):
        
        if hasattr(self, self.method):
            function_ref = getattr(self, self.method)
            values = function_ref(frame, **self.parameters)

            return self.toResults(frame, values)

        featureset = self.findFeatureset(features)
        #this will catch nested features
        
        if not len(featureset):
            return []
         
        if self.featurecriteria.has_key("index"):
            i = int(self.featurecriteria['index'])
            
            if len(featureset) > i:
                featureset = [featureset[i]]
            else:
                return []
        #TODO more advanced filtering options here
        
        values = []
        
        if hasattr(featureset[0], self.method):
            values = [getattr(f, self.method) for f in featureset] 
        
        if featureset[0].featuredata.has_key(self.method):
            values = [f.featuredata[self.method] for f in featureset]
        
        return self.toResults(frame, values)
        
    def findFeatureset(self, features):
        
        fs = []
        for f in features:
            if f.inspection == self.inspection:
                fs.append(f)
                
            if len(f.children):
                fs = fs + self.findFeatureset(f.children)
            
        return fs
        
    def toResults(self, frame, values):
        if not values or not len(values):
            return []
        
        def numeric(val):
            try:
                return float(val)
            except TypeError:
                try:
                    return float(val[0] + val[1] + val[2]) / 3
                except Error:
                    return None

        return [ Result(
            numeric = numeric(v),
            string = str(v),
            capturetime = frame.capturetime,
            camera = frame.camera,
            inspection = self.inspection,
            measurement = self.id,
            frame = frame.id) for v in values ]
    
    def __repr__(self):
        return "<Measurement: " + str(self.inspection) + " " + self.method + " " + str(self.featurecriteria) + ">"
            
from Result import Result
