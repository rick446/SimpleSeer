import gc

import SimpleSeer.models as M


@core.state('start')
def start(state):
    state.core.set_rate(10.0)
    return state.core.state('waitforbuttons')
    
@core.state('waitforbuttons')
def waitforbuttons(state):
    core = state.core
    while True:
        core.tick()
        scan = core.cameras[0]
        if scan.device.email or scan.device.file:
            return state.core.state('scan')

@core.state('scan')
def scan(state):
    core = state.core
    scan = core.cameras[0]
    
    scan.setProperty("resolution", 75)
    scan.setProperty("mode", "gray")
    M.Alert.clear()
    M.Alert.info("Preview scan, Please wait")
    preview = scan.getPreview()
    
    blobs = preview.stretch(25,255).findBlobs(minsize = 250)
    
    if not blobs:
      M.Alert.error("No part found, please reseat part close lid and retry")
      return core.state('waitforbuttons')

    topleft = blobs[-1].mBoundingBox[0:2]
    bottomright = (topleft[0] + blobs[-1].mBoundingBox[2], topleft[1] + blobs[-1].mBoundingBox[3])

    scan.setROI(topleft, bottomright)
    scan.setProperty("resolution", 1200)
    scan.setProperty("mode", "color")
    
    M.Alert.clear()
    M.Alert.info("Scanning.... Please wait")
    id = '' 
    for frame in core.capture():
        img = frame.image
        numpdiff = (img - img.smooth()).getNumpy()
        rows = numpdiff.sum(1)
        rowsums = rows.sum(1)
        thresh = np.mean(rowsums) + np.std(rowsums) * 3
        stripe_rows = np.where(rowsums > thresh)
        if len(stripe_rows[0]):
        nump = img.getNumpy()
        for index in stripe_rows[0]:
            if index == 0 or index == img.width - 1:
                continue
            stripe = nump[index,:]
            channels = np.where(stripe.min(0) > 10)
            for channel in channels:
                nump[index,:,channel] = np.round(np.mean([nump[index-1,:,channel], nump[index+1,:,channel]], 0))
        frame.image = Image(nump)
               
        process(frame)
        frame.save()
        id = frame.id
    scan.setROI()
    M.Alert.clear()
    M.Alert.redirect("frame/" + str(id))
    return core.state('waitforbuttons')

    
def process(frame):
    frame.features = []
    frame.results = []
    for inspection in M.Inspection.objects:
        if inspection.parent:
            return
        if inspection.camera and inspection.camera != frame.camera:
            return
        results = inspection.execute(frame.image)
        frame.features += results
        for m in inspection.measurements:
            m.execute(frame, results)
    
