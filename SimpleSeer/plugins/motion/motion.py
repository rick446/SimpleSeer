import numpy as np

import SimpleCV
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

class MotionFeature(SimpleCV.Feature):
  movement = 0.0

  def __init__(self, image, mval, compared_with=None, top = 0, left = 0, right = -1, bottom = -1):
    #TODO, if parameters are given, crop on both images
    self.image = image
    self.movement = mval
    self.compared = compared_with

    if (right == -1):
      right = image.width

    if (bottom == -1):
      bottom = image.height

    self.points = [(left, top), (right, top), (right, bottom), (left, bottom)]
    self.x = left + self.width() / 2
    self.y = top + self.height() / 2

class Motion(base.InspectionPlugin):
  
  @classmethod
  def coffeescript(cls):
    yield "models/feature", '''
class MotionFeature
  constructor: (feature) ->
    @feature = feature
    
  represent: () =>
    "Motion " + Math.round(@feature.get("featuredata").movement)
    
plugin this, MotionFeature:MotionFeature
'''

  def __call__(self, image):
    SS = util.get_seer()
    if len(SS.lastframes) > 1:
      #TODO, find the index of the named camera
      lastframe = SS.lastframes[-2][0]
      lastimage = lastframe.image
    else:
      return None

    diff = (image - lastimage) + (lastimage - image)

    ff = M.FrameFeature()
    fid = None
    if hasattr(lastframe, "_id"):
      fid = lastframe._id
    ff.setFeature(MotionFeature(image, np.mean(diff.meanColor()), fid))
    return [ff]
