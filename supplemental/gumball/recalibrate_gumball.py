#!/usr/bin/python

from SimpleSeer.Session import Session
Session("/etc/simpleseer.cfg")

from SimpleSeer.models import *
import numpy as np
from scipy.spatial.distance import euclidean as distance


meas = Measurement.objects( method = "closestcolor" )[0]

pallette = meas.parameters['pallette']
colormatches = {}

for f in Frame.objects:
    clr = f.features[0].meancolor  
    detected = f.results[0].string
    if not detected in colormatches:
        colormatches[detected] = []
    colormatches[detected].append(clr)

means = {}
for match in colormatches.keys():
    count = len(colormatches[match])
    mean = np.mean(colormatches[match], 0)
    means[match] = list(mean)
    stdev = np.std(colormatches[match], 0)
    dist = distance(pallette[match], mean)
     
    print "%d %s matches meancolor distance %f std %s " % (count, match, dist, stdev) 

print "new pallette"
print str(means)
