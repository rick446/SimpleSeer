import numpy as np

from SimpleCV import *
from SimpleSeer import models as M
from SimpleSeer import util

from SimpleSeer.plugins import base
"""
Overly simplified template matching plugin

insp = Inspection( name= "SimpleTemplate", 
                   method="simpleTemplate", 
                   camera = "Default Camera")
insp.save()

#Inspection(name="derp7",method="simpleTemplate",parameters={"template":"/home/kscottz/SimpleSeer/SimpleSeer/plugins/SimpleTemplate/template.png"}).save()


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
    threshold = 3
    method = "SQR_DIFF_NORM"

    #this is a temporary hack
    if( not params.has_key('template') ):
      print "Bailing due to lack of template"
      return [] # required param
    else:
      templ=Image(params['template'])
      templates=[templ]


    if( params.has_key('method') ):
      method = params['method'] 

    if( params.has_key('threshold') ):
      threshold = params['threshold']
      
    # we want to optionally supply a count value, if we don't get count
    # number of hits we iterate through the templates, try to match up the 
    # overlapping ones, and then get a final count. 
      
    for t in templates:
      fs = image.findTemplate(t,threshold,method)
      if fs is not None:
        break 

    if fs is not None:
      fs.draw()
      for f in fs: # do the conversion from SCV featureset to SimpleSeer featureset
        ff = M.FrameFeature()
        f.image = None
        f.template = None
        ff.setFeature(f)
        retVal.append(ff)

    if( params.has_key("saveFile") ):
      image.save(params["saveFile"])

    return retVal 

