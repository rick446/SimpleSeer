import numpy as np

import SimpleCV
from SimpleSeer import models as M
from SimpleSeer import util

from SimpleSeer.plugins import base
"""
Overly simplified template matching plugin

insp = Inspection( name= "SimpleTemplate", 
                   method="simpleTemplate", 
                   camera = "Default Camera")
insp.save()


meas = Measurement( name="center", 
                    label="position", #Human readable name 
                    method = "center", #the method to call on a regionFeature
                    parameters = dict(), #not needed - store parameters here
                    units = "pixels", # 
                    featurecriteria = dict( index = 0 ), #not used
                    inspection = insp.id #point back to the original inspection)

meas.save()


"""

class SimpleTemplate(base.InspectionPlugin):
  """
  SimpleTemplate
  
  extraction parameters:
  method = method string - ignore this if you don't know what it is 
  threshold = the top x standard deviations above the mean match, in general 3/4/5 work well
  template = A list of templates from gridfs

  """
  def __call__(self, image):
    params = util.utf8convert(self.inspection.parameters)

    retVal = []
    #we assume all of this is validated and correct 
    templates = [] # get templates from GridFS  
    threshold = 5
    method = "SQR_DIFF_NORM"

    if( params.hasKey('method') ):
      method = params('method') 

    if( params.hasKey('threshold') ):
      threshold = params('threshold') 
      
    # we want to optionally supply a count value, if we don't get count
    # number of hits we iterate through the templates, try to match up the 
    # overlapping ones, and then get a final count. 
      
    for t in templates:
      fs = img.findTemplate(t,threshold,method)
      if fs is not None:
        break 

    if fs is not None:
      fs.draw()
      for f in fs: # do the conversion from SCV featureset to SimpleSeer featureset
        ff = M.FrameFeature()
        ff.setFeature(f)
        retVal.append(ff)

    return retVal 

