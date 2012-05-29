import numpy as np

from SimpleSeer import models as M
from SimpleSeer import util
from SimpleSeer.plugins import base

class Blob(base.InspectionPlugin):

    @classmethod
    def coffeescript(cls):
        yield 'models/inspection', '''
class Blob
  constructor: (inspection) ->
    @inspection = inspection
  run: () =>
    console.log 'Running blob on', @inspection

plugin this, blob:Blob
'''

    def __call__(self, image):
        params = util.utf8convert(self.inspection.parameters)

        # okay I am going to gut this, so it will break stuff.
        # the new method allows the user to use one of the following methods
        #
        # Hue - find things with a certain color
        # Color - find things with a certain color
        # Raw - binary adaptive or blanket threshold - old school blobs
        # FloodFill - pick a pixel and a tolerance - find blob from there 
        #  
        # eventually all of the location based approaches should support multiple locations
        # to sample from 
        #
        # For hue and a raw the user needs to specify a single upper 
        # and lower bound variable. 
        # 
        # For color and flood fill the user can specify both the
        # upper and lower color bound as two precise triplets
        # or as a single triplet as the delta around the color
        # The suggested UI for this 
        # is a color palette in gimp where the user can select a region 
        # around the value ... N.B. eventually we should actually render
        # this stuff in 3D and let people pare down the color cube/cone 
        #
        # The user also has the option to invert the results, and 
        # set the minimum and max size of the blob.
        #
        # If the user provides parameters for multiple of 
        # the above approaches we return None. 

        invert = False
        
        hue = None
        hueLocation = None
        doHue = False
        color = None
        colorLocation = None
        doColor = False
        location = None
        doFF = True 
        thresh1 = None
        thresh2 = None
        
        parse_error = False

        if params.has_key("invert"):
            invert = params["invert"]
            del params["invert"]
        
        #do the parsing for hue distance 
        if( params.has_key("hueLocation")): # I am assuming this is the (x,y) pos of a reference pixel
            hueLoc = tuple(int(item) for item in params['hueLocation'].strip("()").split(","))
            del params["hueLocation"]
            hue = image[hueLoc[0],hueLoc[1]]
            # hue = Color.BGRToHue(hue)
            doHue = True
        elif( params.hasKey("hue")):
            hue = int(params['hue'])
            del params["hue"]
            doHue = True

        if( params.has_key("colorLocation")): # I am assuming this is the (x,y) pos of a reference pixel
            colorLoc = tuple(int(item) for item in params['colorLocation'].strip("()").split(","))
            color = image[colorLoc[0],colorLoc[1]]            
            del params["colorLocation"]
            doColor = True
        elif( params.hasKey("color")):
            color = params['color'].split(",")
            del params["color"]
            doColor = True

        if( params.has_key("location")): # I am assuming this is the (x,y) pos of a reference pixel
            location = tuple(int(item) for item in params['location'].strip("()").split(","))
            del params["location"]
            doFF = True

        #These are for fine grain control of flood fill
        #We can also use them to pick out colors using the createBinaryMask function. 
        if( params.has_key("thresh1") ):
            thresh1 = tuple(int(item) for item in params['thresh1'].strip("()").split(","))
            del params["thresh1"]

        if( params.has_key("thresh2") ):
            thresh1 = tuple(int(item) for item in params['thresh2'].strip("()").split(","))
            del params["thresh2"]


        #now get the other params
        thresh=-1
        blocksize=0
        p=5
        minsize = 10
        maxsize = 0
        if params.has_key("thresh"):
            thresh = params["thresh"]
            del params["thresh"]
        if params.has_key("blocksize"):
            blocksize = params["blocksize"]
            del params["blocksize"]
        if params.has_key("p"):
            p = params["p"]
            del params["p"]

                
        count = 0
        if( doFF ):
            count = count + 1
            if( thresh1 is None ):
                count = count + 1
        if( doHue ):
            count = count + 1
        if( doColor ):
            count = count + 1

        if( count > 1 ): # user gets to specify one operation - if they select two error out
            return []
        
        if( doHue ):#hue distance
            mask = image.hueDistance(hue)
            mask = mask.binarize(thresh=thresh,blocksize=blocksize,p=p)
            # there is a lot more room to do cool stuff in here
        elif( doColor ): #color distance
            mask = image.colorDistance(color)
            mask = mask.binarize(thresh=thresh,blocksize=blocksize,p=p)
            # there is a lot more room to do cool stuff in here
        elif( doFF ):
            #eventually we could pepper an ROI with spots to get more robust results. 
            if( thresh2 is not None):
                mask = image.floodFillToMask(location,lower=thresh1,upper=thresh2)
            else:
                mask = image.floodFillToMask(location,tolerance=thresh1)
        else: #vanilla binarize
            mask = img.binarize(thresh=thresh,blocksize=blocksize,p=p)
        # SUGGEST ALSO USING CREATE BINARY MASK HERE 
        # WE COULD ALSO AUTOGEN MASK USING THE FIND BLOBS FROM PALLETTE IF YOU WANT TO GET FANCY

        if( invert ):
            mask = mask.invert()

        # SUGGEST ADDING AN OPTIONAL DILATE / ERODE HERE
        
        blobs = image.findBlobsFromMask(mask,minsize=minsize,maxsize=maxsize)

        if not blobs:
            return []

        feats = []
        for b in reversed(blobs): #change sort order to big->small
            ff = M.FrameFeature()
            b.image = image
            ff.setFeature(b)
            feats.append(ff)

        return feats

class BlobLength(base.MeasurementPlugin):
    """
    Measurement(name =  "blob_length",
        label = "Blob Area",
        method = "blob_length",
        parameters = dict(),
        featurecriteria = dict( index = 0 ),
        units =  "px",
        inspection = Inspection.objects[0].id).save()
    """

    def __call__(self, frame, featureset):
        return [np.max(eval(featureset[0].featuredata["mMinRectangle"])[1])]

class BlobCount(base.MeasurementPlugin):

    def __call__(self, frame, featureset):
        return [len(featureset)]
