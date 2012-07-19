#!/usr/bin/python

#TODO, NOSEIFY this

#Load session

#load Seer context
from SimpleSeer import Session, SimpleSeer, Inspection, Measurement, Result, Frame, jsonencode
Session("./test_config.cfg")

#initialize the seer
SimpleSeer()

#clear out any existing objects
Frame.objects.delete()
Inspection.objects.delete()
Measurement.objects.delete()
#Watcher.objects.delete()

frame = Frame.capture()[0]  #test capture method
frame.save() #test save
myjson = jsonencode(frame) #test json
frame_loaded = Frame.objects[0] #test load

#initialize inspection
insp = Inspection(
  name = "Area of Interest",
  method = "region",
  camera = "Default Camera",
  parameters = dict( x =  50, y = 50, w = 400, h = 300)) #x,y,w,h

insp.save() #test save
myjson = jsonencode(insp) #test json
insp_loaded = Inspection.objects[0] #test load

features = Inspection.objects[0].execute(Frame.objects[0].image) #test feature extraction
feature = features[0]
myjson = jsonencode(feature) #test json encoding

frame = Frame.objects[0]
frame.features = features
frame.save()  #test save


feature_loaded = Frame.objects[0].features[0] #test load
insp2 = Inspection(
   name = "Light Blobs",
   method = "blob",
   camera = "Default Camera",
   parameters = dict( minsize = 100 ),
   parent = insp.id)

insp2.save()

frames = Inspection.inspect() #an implicit capture event

frames[0].save()  #test save
Frame.objects.order_by("-capturetime").first().features[0].children[0].feature
#reload the most recent frame, and check to see if we can retrieve a blob from it

meas = Measurement(name =  "blob_largest_area",
        label = "Blob Area",
        method = "area",
        parameters = dict(),
        featurecriteria = dict( index = -1 ),
        units =  "px",
        inspection = insp2.id)
meas.save()
results = meas.execute(frames[0])
[r.save() for r in results]


import cherrypy
cherrypy.engine.stop()
#SimpleSeer().stop() 

