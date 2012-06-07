from SimpleSeer import models as M
from SimpleSeer.plugins import base
import SimpleCV


class FaceFeature(SimpleCV.HaarFeature):
    pass


class Face(base.InspectionPlugin):
    
        
  
    @classmethod
    def coffeescript(cls):
        yield 'models/inspection', '''
class Face
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Face Detection"
    
plugin this, face:Face
'''

        yield 'models/feature', '''
class FaceFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/face.png" 
    
  represent: () =>
    "Face Detected at (" + @feature.get("x") + ", " + @feature.get("y") + ")"
    
  tableOk: => true
    
  tableHeader: () =>
    ["Horizontal", "Vertical", "Height", "Width", "Color"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("height"), @feature.get("width"), @feature.get("meancolor")]
    
  render: (pjs) =>
    pjs.stroke 0, 180, 180
    pjs.strokeWeight 3
    pjs.noFill()
    pjs.rect @feature.get('x')-@feature.get('width')/2,@feature.get('y')-@feature.get('height')/2,@feature.get('width'),@feature.get('height'), 4
        
plugin this, FaceFeature:FaceFeature
'''

  
    def __call__(self, image):
        #params = util.utf8convert(self.parameters)
        
        faces = image.findHaarFeatures("face")
        
        if not faces:
            return []
        
        features = []
        
        for f in faces:
            f.__class__ = FaceFeature
            ff = M.FrameFeature()
            ff.setFeature(f)
            features.append(ff)
        
        return features
