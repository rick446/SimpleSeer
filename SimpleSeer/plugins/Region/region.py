from SimpleCV import *
from SimpleSeer import util
from SimpleSeer import models as M

from SimpleSeer.plugins import base

# right now this will act just like a blob the interface should be exactly the same  
#class RegionFeature(SimpleCV.Blob):
#
#    def __init__(self, blob):
#        self = blob

#below are "core" inspection functions
class Region(base.InspectionPlugin):
    # TODO: Have this support unit coordiates (i.e. use floating point numbers versus points)
    def __call__(self, image):
        params = util.utf8convert(self.inspection.parameters)
        retVal = []
        mask = Image((image.width,image.height))
        if( params.has_key('w') and  params.has_key('h') and params.has_key('x') and params.has_key('y') ): #rectangle
            if( params['x'] + params['w'] < image.width and
                params['y'] + params['h'] < image.height and
                params['y'] >= 0 and 
                params['x'] >= 0 ):
                mask.drawRectangle(params['x'],params['y'],params['w'],params['h'],width=-1,color=Color.WHITE)
                mask = mask.applyLayers()
                fs = image.findBlobsFromMask(mask)
                ff = M.FrameFeature()
                if( fs is not None and len(fs) > 0 ):                    
                    fs[-1].draw()
                    ff.setFeature(fs[-1]) # a little hacky but I am sure that it works
                    retVal = [ff]
  
        elif( params.has_key('x') and  params.has_key('y') and params.has_key('r') ): # circle
            if( params['x'] + params['r'] < image.width and
                params['y'] + params['r'] < image.height and 
                params['x'] - params['r'] >= 0 and 
                params['y'] - params['r'] >= 0 ):

                r = params['r']
                x = params['x']
                y = params['y']

                mask.drawCircle((x,y),r,thickness=-1,color=Color.WHITE)
                mask = mask.applyLayers()
                fs = image.findBlobsFromMask(mask)
                ff = M.FrameFeature()
                if( fs is not None and len(fs) > 0 ):                    
                    fs[-1].draw()                   
                    ff.setFeature(fs[-1])
                    retVal = [ff]

        elif( params.has_key('contour') ):
            contour = params['contour'] # this may bail out
            if( len(contour) >=  3 ):
                mask.dl().polygon(contour,filled=True,color=Color.WHITE)
                mask = mask.applyLayers()
                fs = image.findBlobsFromMask(mask)
                ff = M.FrameFeature()
                if( fs is not None and len(fs) > 0 ):                    
                    fs[-1].draw()                   
                    ff.setFeature(fs[-1])
                    retVal = [ff]
            
        if( params.has_key("saveFile") ):
            image.save(params["saveFile"])

        return retVal
