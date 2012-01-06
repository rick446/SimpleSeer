#!/usr/bin/python

#TODO, NOSEIFY this

#Load session

#load Seer context
from SimpleSeer import Session, SimpleSeer, Inspection, Measurement, Result, Frame

#initialize the seer
Session("./test_config.cfg")
SimpleSeer()

#clear out any existing objects
Frame.objects.delete()
Inspection.objects.delete()
Measurement.objects.delete()
#Watcher.objects.delete()

frame = Frame.capture()[0]  #test capture method
frame.save() #test save
myjson = frame.__json__() #test json
frame_loaded = Frame.objects[0] #test load

#initialize inspection
insp = Inspection(
  name = "Area of Interest",
  method = "region",
  camera = "Default Camera",
  parameters = dict( x =  100, y = 100, w = 400, h = 300)) #x,y,w,h

insp.save() #test save
myjson = insp.__json__() #test json
insp_loaded = Inspection.objects[0] #test load

features = Inspection.objects[0].execute(Frame.objects[0].image) #test feature extraction
feature = features[0]
myjson = feature.__json__() #test json encoding

frame = Frame.objects[0]
frame.features = features
frame.save()  #test save

feature_loaded = Frame.objects[0].features[0] #test load

insp2 = Inspection(
   name = "Light Blobs",
   method = "blob",
   camera = "Default Camera",
   parameters = dict( minsize = 1000 ),
   parent = insp.id)

insp2.save()

frames = Inspection.inspect() #an implicit capture event

frames[0].save()  #test save
Frame.objects.order_by("-capturetime").first().features[0].children[0].feature
#reload the most recent frame, and check to see if we can retrieve a blob from it




#TODO, test Redis/Webdis storage
#TODO, call cherrypy controllers

import cherrypy
cherrypy.engine.stop()
#SimpleSeer().stop() 

