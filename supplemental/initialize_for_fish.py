#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session
from os import system

if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "../default.cfg"

Session(config_file)

from SimpleSeer.models.Inspection import Inspection
from SimpleSeer.models.Inspection import Measurement 
from SimpleSeer.models.OLAP import OLAP 
from SimpleSeer.models.Chart import Chart
 

system('echo "db.dropDatabase()" | mongo default')




insp = Inspection( name= "Motion", method="motion")
insp.save()

meas = Measurement( name="movement", label="Movement", method = "movement", parameters = dict(), units = "", featurecriteria = dict( index = 0 ), inspection = insp.id )
meas.save()


## Delivery time
o = OLAP()
o.name = 'Movement'  
o.maxLen = 1000 
o.queryType = 'measurement_id' 
o.queryId = meas.id 
o.fields = ['capturetime','numeric', 'measurement_id', 'inspection_id', 'frame_id']
o.since = None
o.before = None
o.customFilter = {} 
o.statsInfo = []
o.save()

c = Chart()
c.name = 'Movement'
c.olap = o.name
c.style = 'spline'
c.minval = 0
c.maxval = None
c.xtype = 'datetime'
c.colormap = {}
c.labelmap = {}
c.accumulate = False
c.renderorder = 1
c.halfsize = False
c.realtime = True
c.dataMap = ['capturetime','numeric']
c.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c.save()

