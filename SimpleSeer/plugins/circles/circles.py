import numpy as np

import SimpleCV
from SimpleSeer import models as M
from SimpleSeer import util

from SimpleSeer.plugins import base
"""
Overly simplified region detection plugin

insp = Inspection( name= "Circles", 
                   method="corc;es", 
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

class Circle(base.InspectionPlugin):
  """
  line parameters 
  
  extraction parameters:
  length = (minlength,maxlength)
  angle = (minangle,maxangle)
  canny = (lower,upper,threshold) 
  gap = line gap 
  """
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
    if( params.hasKey('canny') ):
      canny = params('canny') 

    if( params.hasKey('distance') ):
      gap = params('distance') 

    if( params.hasKey('radius') ):
      angle = params('radius') 

    if( params.hasKey('threshold') ):
      angle = params('threshold') 
      
    fs = img.findCircles(canny,threshold,distance)

    if fs is not None:
      if( angle[0] is not None):
        fs = FeatureSet(f for f in fs if( f.radius()>=radius[0] ) )
      if( angle[1] is not None ):
        fs = FeatureSet(f for f in fs if( f.radius()<=radius[1] ) )
      fs.draw()
      for f in fs: # do the conversion from SCV featureset to SimpleSeer featureset
        ff = M.FrameFeature()
        ff.setFeature(f)
        retVal.append(ff)

    return retVal 
