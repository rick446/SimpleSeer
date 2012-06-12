import numpy as np
from SimpleCV import *
from SimpleSeer import models as M
from SimpleSeer import util
from SimpleSeer.plugins import base

from SimpleSeer.base import jsonencode
import json

"""
Overly simplified region detection plugin

insp = Inspection( name= "Lines", 
                   method="lines", 
                   camera = "Default Camera")
insp.save()
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


#   @classmethod
#   def coffeescript(cls):
#     yield 'models/inspection', '''
# class Lines
#   constructor: (inspection) ->
#     @inspection = inspection
#   represent: () =>
#     "Lines Detection"
#     #
# plugin this, lines:Lines
# '''

#     yield 'models/feature', '''
# class LineFeature
#   constructor: (feature) ->
#     @feature = feature
   
  
#   icon: () => "/img/line.png" 
    
#   represent: () => " DERP"
#     "asdfasdfasdF"
#  #   "Line Detected at (" + @feature.get("x") + ", " + @feature.get("y") + ") with angle " + @feature.get("featuredata").line_angle + " and length " @feature.get("featuredata").line_length + "."
    
#   tableOk: => true
    
#   tableHeader: () =>
#     ["X Positon", "Y Position", "Angle", "Length", "Color"]
    
#   tableData: () =>
#     [] 
#     #[@feature.get("x"), @feature.get("y"), @feature.get("featuredata").line_angle, @feature.get("featuredata").line_length] #, @feature.get("meancolor")]
    
#   render: (pjs) =>
#     pjs.stroke 0, 180, 180
#     pjs.strokeWeight 3
#     pjs.noFill()
#     pjs.line( @feature.get('featuredata').end_points[0][0],
#               @feature.get('featuredata').end_points[0][1],
#               @feature.get('featuredata').end_points[1][0],
#               @feature.get('featuredata').end_points[1][1] )

# plugin this, Line:LineFeature
# '''

  def __call__(self, image):
    params = util.utf8convert(self.inspection.parameters)    
    # It is just going to be easier to mask over 
    # all of the default params. 
    canny = (50,100) #(cannyth1,cannyth2)
    threshold = 80
    gap = 10
    maxL = int(np.sqrt((image.width*image.width) + (image.height*image.height)))
    length = (30,maxL) # min / max
    angle = (None,None)

    retVal = []

    #we assume all of this is validated and correct 
    if( params.has_key('canny') ):
      canny = params['canny'] 

    if( params.has_key('length') ):
      length = params['length'] 

    if( params.has_key('gap') ):
      gap = params['gap']

    if( params.has_key('angle') ):
      angle = params['angle']

    if( params.has_key('threshold') ):
      angle = params['threshold']
      
    fs = image.findLines(threshold,length[0],gap,canny[0],canny[1])

    if fs is not None:
      if( angle[0] is not None and
          angle[1] is not None ):
        fs = FeatureSet(f for f in fs if( f.angle()>=angle[0] and f.angle()<=angle[1]) ) # filter on the angles 
      if( length[1] is not None ): # we already know that we are greater than the min length
        fs = FeatureSet(f for f in fs if( f.length() <= length[1] ) )
      fs.draw()
      type(fs)
      len(fs)
  
      for f in fs: # do the conversion from SCV featureset to SimpleSeer featureset
        ff = M.FrameFeature()
        ff.setFeature(f)
        retVal.append(ff)

    if( params.has_key("saveFile") ):
      image.save(params["saveFile"])


    return retVal 
