import SimpleCV

from SimpleSeer import util
from SimpleSeer import models as M

from SimpleSeer.plugins import base

class RegionFeature(SimpleCV.Feature):

    def __init__(self, image, startx, starty, width, height):

        point = (startx, starty)
        self.x = point[0] + width / 2
        self.y = point[1] + height / 2
        self.points = [tuple(point),
            (point[0] + width, point[1]),
            (point[0] + width, point[1] + height),
            (point[0], point[1] + height)]

        self.image = image

    def meanColor(self):
        return self.crop().meanColor()

#below are "core" inspection functions
class Region(base.InspectionPlugin):

    def __call__(self, image):
        params = util.utf8convert(self.inspection.parameters)

        if params['x'] + params['w'] > image.width or params['y'] + params['h'] > image.height:
            return []

        ff = M.FrameFeature()
        ff.setFeature(RegionFeature(image, params['x'], params['y'], params['w'], params['h']))
        return [ff]
