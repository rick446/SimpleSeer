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

<<<<<<< HEAD
meas = Measurement( name="Gumball Color", label="Color", method = "closestcolorml", inspection = insp.id )
=======
meas = Measurement( name="Gumball Color", label="Color", method = "closestcolor", inspection = insp.id, parameters = {'ignore': {'black': [128.10160714285715,
   127.26797077922078,
   132.76154220779222],
  'empty': [123.60414772727273, 116.55637175324675, 115.54138798701298]},
 'pallette': {'green': [191.94692370129872,
   195.63243506493507,
   0.5167857142857143],
  'orange': [231.45718344155844, 123.85157467532467, 1.1843587662337662],
  'purple': [174.33642045454545, 147.7037418831169, 161.55934253246753],
  'red': [240.56868506493507, 84.30886363636364, 62.88374188311688],
  'yellow': [224.09747564935066, 177.7784577922078, 0.0034334415584415584]}} )
>>>>>>> 456e1b776ae361fb6db1f7452444193946ed668e
meas.save()

<<<<<<< HEAD
exit()

insp2 = Inspection( name= "Delivery Confirmation",
  method="blobs",
  parameters = { "thresh": 120, "limit": 1 },
  camera = "Delivery Check")
insp2.save()
=======
meas = Measurement( name="Delivery Color", label="Color", method = "closestcolor_manual", inspection = insp.id )
meas.save()
>>>>>>> 9783993c3b85aa7c215c5b1ba910dfb6ead8b9b5

meas3 = Measurement( name="Delivery Time", label="Seconds", method = "timebetween_manual", inspection = insp.id, 
  parameters = dict( inspection = insp.id ))
meas3.save()



## Histogram of color of gumballs evaluated
of1 = OLAPFactory()
qi1 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1}
ci1 = {'accumulate': True, 'name':'column', 'color':'blue', 'minval':0, 'xtype':'linear', 'ticker':10, 'colormap': {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'},'map': {'0': 'red','1': 'green','2': 'yellow','3': 'orange','4': 'purple'},'renderorder':1}
o1 = of1.makeOLAP(queryInfo = qi1, descInfo = None, chartInfo = ci1)
o1.allow = 1000
o1.name = 'Colors Evaluated'
o1.realtime = 1
o1.save()

## Histogram of color of gumballs delivered
of2 = OLAPFactory()
qi2 = {'objType':'measurement', 'objName':'Delivery Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1}
ci2 = {'accumulate': True, 'name':'column', 'color':'blue', 'minval':0, 'xtype':'linear', 'ticker':10, 'colormap': {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'},'map': {'0': 'red','1': 'green','2': 'yellow','3': 'orange','4': 'purple', 'renderorder':2}}
o2 = of2.makeOLAP(queryInfo = qi2, descInfo = None, chartInfo = ci2)
o2.allow = 1000
o2.name = 'Colors Delivered'
o2.realtime = 1
o2.save()

## Delivery time, moving average
of5 = OLAPFactory()
qi5 = {'objType':'measurement', 'objName':'Delivery Time', 'objFields':['capturetimeEpochMS', 'numeric', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
di5 = {'formula':'moving', 'params':['capturetimeEpochMS', 'numeric'], 'window':5, 'trim':True, 'partial':'drop'}
o5 = of5.makeOLAP(queryInfo = qi5, descInfo = di5)
o5.name = 'Delivery Time Moving Average'
o5.allow = 1000
o5.aggregate = 'mean'
o5.realtime = 1
o5.save()

## Yellow gumball delivered
of6 = OLAPFactory()
qi6 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'yellow'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1, 'sinceTime':86400}
di6 = {'formula':'movingCount', 'params':['capturetimeEpochMS', 'string'], 'window':86400, 'trim':False, 'partial':'drop'}
ci6 = {'minval':0, 'maxval':None, 'color':'yellow', 'renderorder':3, 'name':'spline'}
o6 = of6.makeOLAP(queryInfo = qi6, descInfo = di6, chartInfo=ci6)
o6.allow = 1000
o6.name = 'Candies Delivered'
o6.realtime = 1
o6.save()

## Green gumball delivered
of7 = OLAPFactory()
qi7 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'green'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1, 'sinceTime':86400}
di7 = {'formula':'movingCount', 'params':['capturetimeEpochMS', 'string'], 'window':86400, 'trim':False, 'partial':'drop'}
ci7 = {'minval':0, 'maxval':None, 'color':'green', 'name':'spline', 'chartid':o6.id}
o7 = of7.makeOLAP(queryInfo = qi7, descInfo = di7, chartInfo=ci7)
o7.allow = 1000
o7.name = 'Green Candies'
o7.realtime = 1
o7.save()

## Purple gumball delivered
of8 = OLAPFactory()
qi8 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'purple'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1, 'sinceTime':86400}
di8 = {'formula':'movingCount', 'params':['capturetimeEpochMS', 'string'], 'window':86400, 'trim':False, 'partial':'drop'}
ci8 = {'minval':0, 'maxval':None, 'color':'purple', 'name':'spline', 'chartid':o6.id}
o8 = of8.makeOLAP(queryInfo = qi8, descInfo = di8, chartInfo=ci8)
o8.allow = 1000
o8.name = 'Purple Candies'
o8.realtime = 1
o8.save()


## Orange gumball delivered
of8 = OLAPFactory()
qi8 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'orange'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1, 'sinceTime':86400}
di8 = {'formula':'movingCount', 'params':['capturetimeEpochMS', 'string'], 'window':86400, 'trim':False, 'partial':'drop'}
ci8 = {'minval':0, 'maxval':None, 'color':'orange', 'name':'spline', 'chartid':o6.id}
o8 = of8.makeOLAP(queryInfo = qi8, descInfo = di8, chartInfo=ci8)
o8.allow = 1000
o8.name = 'Orange Candies'
o8.realtime = 1
o8.save()

## Red gumball delivered
of9 = OLAPFactory()
qi9 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'filter':{'field':'string', 'val':'red'}, 'since':None, 'before':None, 'limit':1000, 'required':None, 'cton':1, 'sinceTime':86400}
di9 = {'formula':'movingCount', 'params':['capturetimeEpochMS', 'string'], 'window':86400, 'trim':False, 'partial':'drop'}
ci9 = {'minval':0, 'maxval':None, 'color':'red', 'name':'spline', 'chartid':o6.id}
o9 = of9.makeOLAP(queryInfo = qi9, descInfo = di9, chartInfo=ci9)
o9.allow = 1000
o9.name = 'Red Candies'
o9.realtime = 1
o9.save()

## PassFail
of10 = OLAPFactory()
qi10 = {'objType':'measurement', 'objName':'Gumball Color', 'objFields':['capturetimeEpochMS', 'string', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None, 'passfail':1}
ci10 = {'minval':0, 'maxval':None, 'name':'marbleoverview', 'renderorder':1}
o10 = of10.makeOLAP(queryInfo = qi10, descInfo = None, chartInfo=ci10)
o10.allow = 1000
o10.name = 'Candies Overview'
o10.realtime = 1
o10.save()
