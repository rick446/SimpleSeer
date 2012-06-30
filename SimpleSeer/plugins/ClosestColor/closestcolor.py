from SimpleSeer import models as M
from SimpleSeer.plugins import base
from SimpleCV import Color
from scipy.spatial.distance import euclidean as distance

"""

This plugin maps an inspections mean color with a color label based
on a pallette of tuples

Example of a red/green tester:

insp = Inspection( name= "Region", 
  method="region", 
  parameters = { "x": 100, "y": 100, "w": 440, "h": 280 })
insp.save()

meas = Measurement( name= "Color", method="closestcolor",
  inspection = insp.id,
  parameters = { 
    "pallette" : {
      "red" : (255, 0, 0),
      "green" : (0, 255, 0) },
    "ignore" : {
      "blue" : (0,0,255),
      "black" : (0,0,0),
      "white" : (255,255,255)
    }
  })
meas.save()

"""

class ClosestColorMeasurement(base.MeasurementPlugin):

    def __call__(self, frame, features):
        results = []
        params = self.measurement.parameters
        pallette = {}
        if "pallette" in params:
            pallette = params["pallette"]
        else:
            pallette = dict(
                red = Color.RED,
                green = Color.GREEN,
                blue = Color.BLUE,
                yellow = Color.YELLOW,
                violet = Color.VIOLET,
                tan = Color.TAN,
                orange = Color.ORANGE,
                white = Color.WHITE,
                black = Color.BLACK
            )
            
        ignore = {}
        if "ignore" in params:
            ignore = params["ignore"]
        else:
            ignore = dict(
                white = Color.WHITE,
                black = Color.BLACK
            )
        
        maxdist = 9999.0    
        if "maxdistance" in params:
            maxdist = maxdistance
    
        for f in features:
            mindist = 9999.0
            minname = ""
            for name, value in dict(pallette.items() + ignore.items()).items():
                dist = distance(f.meancolor, value) #TODO, use hue matching
                if dist < mindist and dist < maxdist:
                    mindist = dist
                    minname = name
                    
            if minname and not minname in ignore:
                results.append(minname)                
            #TODO: isn't going to work clean with multiple features
            #needs a way to key into featureset
                    
        return results
