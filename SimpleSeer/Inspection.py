from base import *
from Session import *

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
    
    insp = Inspection(dict(
        name = "Blob Measurement 1",
        test_type = "Measurement",
        enabled = 1,
        method = "fixed_window",
        camera = "Default Camera",
        parameters = dict( x =  100, y = 100, w = 400, h = 300))) #x,y,w,h

    insp.save()
    
    Measurement(..., inspection_id = insp.id )
    
    results = insp.execute()
    
    """
    name = mongoengine.StringField()
    test_type = mongoengine.StringField() 
    method = mongoengine.StringField()
    enabled = mongoengine.IntField()
    camera = mongoengine.StringField()
    parameters = mongoengine.DictField()


                         
    def execute(self, frame):
        """
        The execute method takes in a frame object, executes the method
        and sends the samples to each measurement object.  The results are returned
        as a multidimensional array [ samples ][ measurements ] = result
        """

        roi_function_ref = getattr(self, self.method)
        #get the ROI function that we want
        #note that we should validate/roi method

                
        samplesroi = roi_function_ref(frame)
        
        if not samplesroi:
            return
            
        samples, roi = samplesroi
        #NATE ROI SHOULD ALSO BE AN ARRAY TODO
            
        if not isinstance(samples, list):
            samples = [samples]
        
        results = []
        frame.image.addDrawingLayer()
        for sample in samples:
            sampleresults = []
            for m in self.measurements:
                r = m.calculate(sample)
                     
                r.roi = roi
                r.capturetime = frame.capturetime
                r.camera = frame.camera
                r.frame_id = frame._id
                r.inspection_id = self._id
                r.measurement_id = m._id
                    
                sampleresults.append(r)
                #probably need to add unit conversion here
            
            results.append(sampleresults)
            frame.image.dl().blit(sample.applyLayers(), (roi[0], roi[1]))

        return results
        
    @property
    def measurements(self):
        #note, should figure out some way to cache this
        return Measurement.find( inspection_id = self._id ).all()

    #@classmethod
    #def find(cls, *args, **kwargs):
        #if not kwargs.has_key('enabled'):
        #   kwargs['enabled'] = 1
        
     #   return cls.m.find(*args, **kwargs)

    def __json__(self):
        return json.dumps(dict( name = self.name, test_type = self.test_type, enabled = self.enabled, method = self.method ))
    

    #below are "core" inspection functions
    def fixed_window(self, frame):        
        params = self.parameters
        return ([frame.image.crop(**params)], [tuple(params[x], params[y])])
        
    def blob_detection(self, frame):
        params = self.parameters
        blobs = frame.image.findBlobs(**params)
        if not blobs:
            return 
        return ([b.crop() for b in blobs], [b.points[0] for b in blobs])


from Measurement import Measurement
