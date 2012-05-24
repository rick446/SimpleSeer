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

        #if we have a color parameter, lets threshold
        blobs = []
        invert = False
        pixel = ""
        if params.has_key("invert"):
            invert = params["invert"]
            del params["invert"]

        if params.has_key("pixel"):
            pixel = params['pixel'].split(",")
            del params["pixel"]

        if params.has_key("hue"):
            image = image.hueDistance(int(params["hue"])).invert()
            del params["hue"]

        if pixel:
            color = str(image.getPixel(int(pixel[0]), int(pixel[1])))[1:-1]
            params["color"] = color
            self.inspection.parameters["color"] = color
            del self.inspection.parameters["pixel"]
            if self.inspection.id:
                self.inspection.save()

        if params.has_key("color"):
            r,g,b = params["color"].split(",")
            image = image.colorDistance((float(r), float(g), float(b))).invert()
            del params["color"]

        if invert:
            blobs = image.invert().findBlobs(**params)
        else:
            blobs = image.findBlobs(**params)

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
