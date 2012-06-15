#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session

if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "gumball.cfg"

Session(config_file)

from SimpleSeer.models import Inspection, Measurement, Frame, OLAP, Result
from SimpleSeer.models import Result, Inspection, Measurement, Frame
from SimpleSeer.models.OLAP import OLAP, OLAPFactory
 

Frame.objects.delete()
Inspection.objects.delete()
Measurement.objects.delete()
OLAP.objects.delete()
Result.objects.delete()

insp = Inspection( name= "Region", 
  method="region", 
  parameters = { "x": 100, "y": 100, "w": 440, "h": 280 }, 
   camera='Color Check')
insp.save()

meas = Measurement( name="Gumball Color", label="Color", method = "closestcolor", inspection = insp.id )
meas.save()

meas = Measurement( name="Delivery Color", label="Color", method = "closestcolor_manual", inspection = insp.id )
meas.save()

m
meas3 = Measurement( name="Delivery Time", label="Seconds", method = "timebetween_manual", inspection = insp.id, 
  parameters = dict( inspection = insp.id ))
meas3.save()



## Histogram of color of gumballs evaluated
of1 = OLAPFactory()
qi1 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1}
ci1 = {'name':'sumbucket', 'color':'blue', 'minval':0, 'xtype':'linear', 'ticker':10}
o1 = of1.makeOLAP(queryInfo = qi1, descInfo = None, chartInfo = ci1)
o1.allow = 1000
o1.name = 'ColorEvaled'
o1.realtime = 1
o1.save()

## Histogram of color of gumballs delivered
#of2 = OLAPFactory()
#qi2 = {'objType':'measurement', 'objName':'Delivery Color', 'objFields':['string', 'capturetimeEpochMS', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
#ci2 = {'name':'sumbucket', 'color':'blue', 'minval':0, 'xtype':'linear', 'ticker':10}
#o2 = of2.makeOLAP(queryInfo = qi2, descInfo = None, chartInfo = ci2)
#o2.allow = 1000
#o2.name = 'ColorDelivered'
#o2.realtime = 1
#o2.save()

## Diameter of gumballs delivered
of3 = OLAPFactory()
qi3 = {'objType':'measurement', 'objName':'Delivery Radius', 'objFields':['capturetimeEpochMS', 'numeric', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
o3 = of3.makeOLAP(queryInfo = qi3, descInfo = None)
o3.allow = 1000
o3.name = 'GumballDiameter'
o3.realtime = 1
o3.save()

## Histogram of diameter of gumballs delivered
of4 = OLAPFactory()
qi4 = {'objType':'measurement', 'objName':'Delivery Radius', 'objFields':['capturetimeEpochMS', 'numeric', 'inspection', 'frame', 'measurement', 'id'], 'round': [2, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
ci4 = {'name':'sumbucket', 'color':'blue', 'minval':0, 'xtype':'linear', 'ticker':10}
o4 = of4.makeOLAP(queryInfo = qi4, descInfo = None, chartInfo = ci4)
o4.allow = 1000
o4.name = 'GumballDiameterHist'
o4.realtime = 1
o4.save()

## Delivery time, moving average
of5 = OLAPFactory()
qi5 = {'objType':'measurement', 'objName':'Delivery Time', 'objFields':['capturetimeEpochMS', 'numeric', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
di5 = {'formula':'moving', 'params':['capturetimeEpochMS', 'numeric'], 'window':5, 'trim':True, 'partial':'drop'}
o5 = of5.makeOLAP(queryInfo = qi5, descInfo = di5)
o5.name = 'DeliveryTimeMovingAverage'
o5.allow = 1000
o5.aggregate = 'mean'
o5.realtime = 1
o5.save()

## Yellow gumball delivered
of6 = OLAPFactory()
qi6 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'yellow'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1}
ci6 = {'minval':0, 'maxval':0}
o6 = of6.makeOLAP(queryInfo = qi6, descInfo = None, chartInfo=ci6)
o6.allow = 1000
o6.name = 'YellowOnly'
o6.realtime = 1
o6.save()

## Green gumball delivered
of7 = OLAPFactory()
qi7 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'green'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1}
ci7 = {'minval':0, 'maxval':0}
o7 = of7.makeOLAP(queryInfo = qi7, descInfo = None, chartInfo=ci7)
o7.allow = 1000
o7.name = 'GreenOnly'
o7.realtime = 1
o7.save()

## Blue gumball delivered
of8 = OLAPFactory()
qi8 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'blue'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1}
ci8 = {'minval':0, 'maxval':0}
o8 = of8.makeOLAP(queryInfo = qi8, descInfo = None, chartInfo=ci8)
o8.allow = 1000
o8.name = 'BlueOnly'
o8.realtime = 1
o8.save()

## Red gumball delivered
of9 = OLAPFactory()
qi9 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'red'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1}
ci9 = {'minval':0, 'maxval':0}
o9 = of9.makeOLAP(queryInfo = qi9, descInfo = None, chartInfo=ci9)
o9.allow = 1000
o9.name = 'RedOnly'
o9.realtime = 1
o9.save()

## PassFail
of10 = OLAPFactory()
qi10 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None, 'passfail':1}
o10 = of10.makeOLAP(queryInfo = qi10, descInfo = None)
o10.allow = 1000
o10.name = 'GumballPassFail'
o10.realtime = 1
o10.save()
