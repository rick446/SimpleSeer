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
from SimpleSeer import models as M
from SimpleSeer.plugins import base

class Barcode(base.InspectionPlugin):

  def __call__(self, image):
    code = self.image.findBarcode()

    if not code:
      return []

    feats = []
    for f in code:
      ff = M.FrameFeature()
      code.image = image
      ff.setFeature(f)
      feats.append(ff)

    return feats
