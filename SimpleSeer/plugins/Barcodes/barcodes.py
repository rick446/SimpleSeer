'''

  To add a barcode inspection, at the simpleseer command line run:

  >>> insp = Inspection(
        name = "Barcode",
        method = "barcode",
        camera = "Default Camera",
      )

  Then to save to the database:

  >>> insp.save()
'''
from SimpleCV import *
from SimpleSeer import util
from SimpleSeer import models as M
from SimpleSeer.plugins import base

class Barcodes(base.InspectionPlugin):

  def __call__(self, image):
    params = util.utf8convert(self.inspection.parameters)

    code = image.findBarcode()

    if not code:
      return []

    feats = []
    for f in code:
      f.draw()
      ff = M.FrameFeature()
      code.image = image
      ff.setFeature(f)
      feats.append(ff)

    if( params.has_key("saveFile") ):
      image.save(params["saveFile"])

    return feats
