from SimpleSeer.base import *
from SimpleSeer.plugins.base import *
import numpy as np

"""
Overly simplified motion detection plugin
insp = Inspection( name= "Motion", method="motion", camera = "Default Camera")
insp.save()

meas = Measurement( name="movement", label="Movement", method = "movement", parameters = dict(), units = "", featurecriteria = dict( index = 0 ), inspection = insp.id )
meas.save()


"""

class Motion(SimpleCV.Feature):
  movement = 0.0

  def __init__(self, image, mval, top = 0, left = 0, right = -1, bottom = -1):
    #TODO, if parameters are given, crop on both images
    self.image = image
    self.movement = mval

    if (right == -1):
      right = image.width

    if (bottom == -1):
      bottom = image.height
  
    self.points = [(left, top), (right, top), (right, bottom), (left, bottom)]
    self.x = left + self.width() / 2
    self.y = top + self.height() / 2 
  
def motion(self, image):
  SS = SimpleSeer()
  if len(SS.lastframes) > 1:
    #TODO, find the index of the named camera
    lastimage = SS.lastframes[-2][0].image
  else:
    return None

  diff = (image - lastimage) + (lastimage - image)
  
  ff = FrameFeature()
  ff.setFeature(Motion(image, np.mean(diff.meanColor())))
  return [ff]

M.Inspection.motion = motion
from SimpleSeer.SimpleSeer import SimpleSeer
