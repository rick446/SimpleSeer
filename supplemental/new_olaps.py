#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session

if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "../default.cfg"

Session(config_file)

from SimpleSeer.models.OLAP import OLAP
from SimpleSeer.models.Chart import Chart
from bson import ObjectId

OLAP.objects.delete()
Chart.objects.delete()

o = OLAP()
o.name = 'Test OLAP'  
o.maxLen = 1000 
o.queryType = 'measurement' 
o.queryId = ObjectId('4fdbac481d41c834fb000001') 
o.fields = ['capturetime','string']
o.groupTime = 'minute'
o.valueMap = {}
o.since = None
o.before = None
o.customFilter = {} 
o.statsInfo = [{'sum': 1},
               {'min': 'string'},
               {'max': 'string'}]
o.save()


c = Chart()
c.name = 'Colors Evaluated'
c.olap = o.name
c.style = 'column'
c.minval = 0
c.maxval = 10
c.xtype = 'linear'
c.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c.labelmap = {'0': 'red','1': 'green','2': 'yellow','3': 'orange','4': 'purple'}
c.accumulate = True
c.renderorder = 2
c.halfsize = True
c.realtime = True

c.save()
