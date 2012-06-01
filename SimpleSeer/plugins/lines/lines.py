import numpy as np

import SimpleCV
from SimpleSeer import models as M
from SimpleSeer import util
from SimpleSeer.base import jsonencode
from SimpleSeer.plugins import base

"""
Overly simplified region detection plugin

insp = Inspection( name= "Lines", 
                   method="lines", 
                   camera = "Default Camera")
insp.save()


meas = Measurement( name="length", 
                    label="length", #Human readable name 
                    method = "length", #the method to call on a regionFeature
                    parameters = dict(), #not needed - store parameters here
                    units = "pixels", # 
                    featurecriteria = dict( index = 0 ), #not used
                    inspection = insp.id #point back to the original inspection)

meas.save()


"""

class Lines(base.InspectionPlugin):
  """
  line parameters 
  
  extraction parameters:
  length = (minlength,maxlength)
  angle = (minangle,maxangle)
  canny = (lower,upper,threshold) 
  gap = line gap 
  """
  def __call__(self, image):
    print "HELLO FROM LINES"
    params = util.utf8convert(json.loads(jsonencode(self.inspection.parameters)))    
    print "HELLO FROM LINES"
    # It is just going to be easier to mask over 
    # all of the default params. 
    canny = (50,100) #(cannyth1,cannyth2)
    threshold = 80
    gap = 10
    maxL = int(sqrt((image.width*image.width) + (image.height*image.height)))
    length = (30,maxL) # min / max
    angle = (None,None)

    retVal = []

    #we assume all of this is validated and correct 
    if( params.hasKey('canny') ):
      canny = params('canny') 

    if( params.hasKey('length') ):
      length = params('length') 

    if( params.hasKey('gap') ):
      gap = params('gap') 

    if( params.hasKey('angle') ):
      angle = params('angle') 

    if( params.hasKey('threshold') ):
      angle = params('threshold') 
      
    fs = img.findLines(threshold,length[0],gap,canny[0],canny[1])

    if fs is not None:
      if( angle[0] is not None and
          angle[1] is not None ):
        fs = FeatureSet(f for f in fs if( f.angle()>=angle[0] and f.angle()<=angle[1]) ) # filter on the angles 
      if( length[1] is not None ): # we already know that we are greater than the min length
        fs = FeatureSet(f for f in fs if( f.length() <= length[1] ) )
      fs.draw()
      for f in fs: # do the conversion from SCV featureset to SimpleSeer featureset
        ff = M.FrameFeature()
        ff.setFeature(f)
        retVal.append(ff)

    if( params.has_key("saveFile") ):
      image.save(params["saveFile"])


    return retVal 
