from SimpleSeer import models as M
from SimpleSeer.plugins import base

class Face(base.InspectionPlugin):
  
    def __call__(self, image):
        #params = util.utf8convert(self.parameters)
        
        faces = image.findHaarFeatures("face")
        
        if not faces:
            return []
        
        features = []
        
        for f in faces:
            ff = M.FrameFeature()
            ff.setFeature(f)
            features.append(ff)
        
        return features