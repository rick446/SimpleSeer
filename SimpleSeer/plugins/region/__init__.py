from SimpleSeer.plugins.base import *

class Region(SimpleCV.Feature):
    
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
def region(self, image):        
    params = utf8convert(self.parameters)
    
    if params['x'] + params['w'] > image.width or params['y'] + params['h'] > image.height:
        return []
    
    ff = FrameFeature()
    ff.setFeature(Region(image, params['x'], params['y'], params['w'], params['h']))
    return [ff]
    
    
M.Inspection.region = region
