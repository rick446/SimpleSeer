#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session

if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "../default.cfg"

Session(config_file)

from SimpleSeer.models.OLAP import OLAP, OLAPFactory
 
OLAP.objects.delete()

of = OLAPFactory()

qi = {'objType':'inspection', 'objName':'Motion', 'objFields':['capturetimeEpochMS', 'numeric', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
dimoving = {'formula':'moving', 'params':['capturetimeEpochMS', 'numeric'], 'window':5, 'trim':True, 'partial':'drop'}
qihist = {'objType':'inspection', 'objName':'Motion', 'objFields':['numeric', 'capturetimeEpochMS', 'inspection', 'frame', 'measurement', 'id'], 'round': [10, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
cihist = {'name':'sumbucket', 'color':'blue', 'minval':0, 'xtype':'linear', 'ticker':10} 


omove = of.makeOLAP(queryInfo = qi, descInfo = dimoving)
omove.name = 'MotionMovingAverage'
omove.allow = 1000
omove.aggregate = 'mean'
omove.realtime = 1
omove.save()

ohist = of.makeOLAP(queryInfo = qihist, descInfo = None, chartInfo = cihist)
ohist.name = 'MotionHistogram'
ohist.allow = 1000
ohist.aggregate = 'mean'
ohist.realtime = 0
ohist.save()

oraw = of.makeOLAP(queryInfo = qi, descInfo = None)
oraw.allow = 100
oraw.aggregate = 'median'
oraw.name = 'Motion'
oraw.realtime = 1
oraw.save()

