
#
def Inspection.face_detection(self, frame):
    return frame.image.findHaarFeatures("/usr/local/share/opencv/haarcascades/haarcascade_frontalface_alt.xml").crop()

def Inspection.find_center_fiducial(self, frame):
    params = self.parameters
    
    blobs = frame.image.findBlobs(**params['blob_params'])
    if not blobs:
        return ['']
    
    matches = []
    
    rad = params['radius']
    for b in blobs.filter(blobs.x > rad & blobs.y > rad & frame.image.width - blobs.x > rad & frames.image.height - blobs.y > rad):
        if b.match(params['reference_object']) < params['match_thresh']:
           matches.append(b) 
    
    if not len(matches):
        return ['']
    
    return [frame.crop(m.x - rad, m.y - rad, rad*2, rad*2) for m in matches]
    
    



def Measurement.eye_distances(self, img):
    
    eyes = img.findHaarFeatures("/usr/local/share/opencv/haarcascades/haarcascade_eye.xml")
    if not eyes or len(eyes) != 2:
        return ['']
    return [eyes.distancePairs()[0][1] / img.width]
    

DEFAULT_FACE_DETECTOR = Inspection(dict(
    name = "Find Faces",
    test_type = "Measurement",
    enabled = 1,
    roi_method = "face_detection",
    camera = "Default Camera",
    roi_parameters = []))

DEFAULT_FACE_DETECTOR_MEASUREMENT = Measurement(dict( 
    name =  "measure_eye_distances",
    label = "Relative eye distances",
    test_method = "eye_distances",
    parameters = dict(),
    result_labels = ["distance"],
    is_numeric = 1,
    units =  "ratio",
    inspection_id = DEFAULT_FACE_DETECTOR._id))
