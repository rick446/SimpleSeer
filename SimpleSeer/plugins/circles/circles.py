import numpy as np

from SimpleCV import *
from SimpleSeer import models as M
from SimpleSeer import util

from SimpleSeer.plugins import base
"""
Overly simplified region detection plugin

insp = Inspection( name= "Circles", 
                   method="circles", 
                   camera = "Default Camera")
insp.save()


meas = Measurement( name="radius", 
                    label="radius", #Human readable name 
                    method = "radius", #the method to call on a regionFeature
                    parameters = dict(), #not needed - store parameters here
                    units = "pixels", # 
                    featurecriteria = dict( index = 0 ), #not used
                    inspection = insp.id #point back to the original inspection)

meas.save()


"""

class Circles(base.InspectionPlugin):
  @classmethod
  def coffeescript(cls):
    yield 'models/inspection', '''
class Circles
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Circle Detection"
    #
plugin this, circles:Circles
'''

    yield 'models/feature', '''
class CircleFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/circle.png" 
    
  represent: () =>
    "Circle Detected at (" + @feature.get("x") + ", " + @feature.get("y") + ") with radius " + @feature.get("featuredata").r
    
  tableOk: => true
    
  tableHeader: () =>
    ["X Positon", "Y Position", "Radius"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("featuredata").r]
    
  render: (pjs) =>
    pjs.stroke 0, 180, 180
    pjs.strokeWeight 3
    pjs.noFill()
    pjs.ellipse( @feature.get('x'), @feature.get('y'), @feature.get('featuredata').r*2, @feature.get('featuredata').r*2 )
plugin this, Circle:CircleFeature
'''
  def __call__(self, image):
    params = util.utf8convert(self.inspection.parameters)
    
    # It is just going to be easier to mask over 
    # all of the default params. 
    canny = 100 
    threshold = 350
    distance = -1
    radius = (None,None)

    retVal = []

    #we assume all of this is validated and correct 
    if( params.has_key('canny') ):
      canny = params['canny'] 

    if( params.has_key('distance') ):
      distance = params['distance']

    if( params.has_key('radius') ):
      radius = params['radius']

    if( params.has_key('threshold') ):
      threshold = params['threshold'] 
      
    fs = image.findCircle(canny,threshold,distance)

    if fs is not None:
      if( radius[0] is not None):
        fs = FeatureSet(f for f in fs if( f.radius()>=radius[0] ) )
      if( radius[1] is not None ):
        fs = FeatureSet(f for f in fs if( f.radius()<=radius[1] ) )
      fs.draw(width=3)
      for f in fs: # do the conversion from SCV featureset to SimpleSeer featureset
        ff = M.FrameFeature()
        ff.setFeature(f)
        retVal.append(ff)

    if( params.has_key("saveFile") ):
      image.save("derp.png")
      image.save(params["saveFile"])

    return retVal 
