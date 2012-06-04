import numpy as np

from SimpleCV import *
from SimpleSeer import models as M
from SimpleSeer import util

from SimpleSeer.plugins import base

"""
Overly simplified motion detection plugin
insp = Inspection( name= "Motion", method="motion", camera = "Default Camera")
insp.save()

meas = Measurement( name="movement", label="Movement", method = "movement", parameters = dict(), units = "", featurecriteria = dict( index = 0 ), inspection = insp.id )
meas.save()


"""

class OCRFeature(SimpleCV.Feature):
  text = ""

  def __init__(self, image,text, top = 0, left = 0, right = -1, bottom = -1):
    #TODO, if parameters are given, crop on both images
    self.image = image

    if (right == -1):
      right = image.width

    if (bottom == -1):
      bottom = image.height

    self.points = [(left, top), (right, top), (right, bottom), (left, bottom)]
    self.x = left + self.width() / 2
    self.y = top + self.height() / 2
    self.text = text 

    def getText(self):
      return self.text

class OCR(base.InspectionPlugin):
  def __call__(self, image):
    params = util.utf8convert(self.inspection.parameters)
    retVal = []

    myWords = image.readText()

    ff = M.FrameFeature()
    ff.setFeature(OCRFeature(image,myWords))
    retVal.append(ff)

    if( params.has_key("saveFile") ):
      image.drawText(myWords,20,20,color=Color.RED)
      image.save(params["saveFile"])

    return retVal 

