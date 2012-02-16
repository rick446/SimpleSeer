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

from SimpleSeer.plugins.base import *
  
        
def barcode(self, image):        
  code = image.findBarcode()
  
  if not code:
    return []

  feats = []
  for f in code:
    ff = FrameFeature()
    code.image = image
    ff.setFeature(f)
    feats.append(ff)
    
  return feats

    
Inspection.barcode = barcode
