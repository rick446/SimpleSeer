from SimpleSeer.base import *
from SimpleSeer.Session import *
from SimpleSeer.FrameFeature import FrameFeature
from SimpleSeer.Inspection import Inspection


def blob(self, image):
		params = utf8convert(self.parameters)
		
		
		#if we have a color parameter, lets threshold        
		blobs = []
		invert = False
		if params.has_key("invert"):
				invert = params["invert"]
				del params["invert"]
				
		if invert:
				blobs = image.invert().findBlobs(**params)
		else:    
				blobs = image.findBlobs(**params)
		
		if not blobs:
				return []
		
		feats = []
		for b in blobs:
				ff = FrameFeature()
				b.image = image
				ff.setFeature(b)
				feats.append(ff)
				
		return feats


Inspection.blob = blob
