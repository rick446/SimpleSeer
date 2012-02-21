from SimpleSeer.plugins.base import *
import numpy as np

def blob(self, image):
    params = utf8convert(self.parameters)
    
    #if we have a color parameter, lets threshold        
    blobs = []
    invert = False
    pixel = ""
    if params.has_key("invert"):
        invert = params["invert"]
        del params["invert"]
    
    if params.has_key("pixel"):
        pixel = params['pixel'].split(",")
        del params["pixel"]
    
    if pixel:
        image = image.colorDistance(image.getPixel(int(pixel[0]), int(pixel[1]))).invert()
        
    if invert:
        blobs = image.invert().findBlobs(**params)
    else:    
        blobs = image.findBlobs(**params)
        
    if not blobs:
        return []
    
    feats = []
    for b in reversed(blobs): #change sort order to big->small
        ff = FrameFeature()
        b.image = image
        ff.setFeature(b)
        feats.append(ff)
        
    return feats

Inspection.blob = blob

"""
    Measurement(name =  "blob_length",
        label = "Blob Area",
        method = "blob_length",
        parameters = dict(),
        featurecriteria = dict( index = 0 ),
        units =  "px",
        inspection = Inspection.objects[0].id).save()
"""

def blob_length(self, frame, featureset):            
    return [np.max(eval(featureset[0].featuredata["mMinRectangle"])[1])]
    
Measurement.blob_length = blob_length

    
def blob_count(self, frame, featureset):            
    return [len(featureset)]
    
Measurement.blob_count = blob_count
    
    
    
