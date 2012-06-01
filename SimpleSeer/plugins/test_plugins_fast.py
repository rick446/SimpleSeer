#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session
#import logging.config


if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "../../default.cfg"

Session(config_file)
#logging.config.fileConfig("../../logging.ini")

from SimpleSeer.models.Inspection import Inspection
from SimpleSeer.models.Inspection import Measurement 
from SimpleSeer.models.OLAP import OLAP 
from SimpleSeer.SimpleSeer import SimpleSeer

from SimpleCV import *

SimpleSeer()
result = []
a = Inspection(name="derp",method="blob", parameters={"invert":True, "saveFile":"test1.png"}).execute(Image("./testdata/rat1.png"))
result.append(a)

b = Inspection(name="derp",method="blob", parameters={"invert":False,"saveFile":"test2.png"}).execute(Image("./testdata/rat1.png"))
result.append(b)

i = Image("./testdata/rat1.png")
c = Inspection(name="derp",method="blob", parameters={"invert":True,"hueLocation":[240,180],"saveFile":"test3.png"}).execute(i)
result.append(c)

d = Inspection(name="derp",method="blob", parameters={"invert":False, "hueLocation":[240,180],"saveFile":"test4.png"}).execute(Image("./testdata/rat1.png"))
result.append(d)

e  = Inspection(name="derp",method="blob", parameters={"invert":False, "hue":0,"saveFile":"test5.png"}).execute(Image("./testdata/rat1.png"))
result.append(e)

f  = Inspection(name="derp",method="blob", parameters={"invert":True, "color":[255,0,0],"saveFile":"test6.png"}).execute(Image("./testdata/rat1.png"))
result.append(f)

g  = Inspection(name="derp",method="blob", parameters={"invert":True, "colorLocation":[240,180],"saveFile":"test7.png"}).execute(Image("./testdata/rat1.png"))
result.append(g)

h  = Inspection(name="derp",method="blob", parameters={"invert":True, "location":[150,150],"thresh1":10,"saveFile":"test8.png"}).execute(Image("./testdata/rat1.png"))
result.append(h)

j  = Inspection(name="derp",method="blob", parameters={"invert":True, "hue":0,"saveFile":"test9.png"}).execute(Image("./testdata/rat1.png"))
result.append(j)

print "Doing lines now... er finding lines."

k  = Inspection(name="lines",method="lines", parameters={"saveFile":"test10.png"}).execute(Image("./testdata/lines.png"))
result.append(k)

l  = Inspection(name="derp",method="lines", parameters={"canny":[1,200],"saveFile":"test11.png"}).execute(Image("./testdata/lines.png"))
result.append(l)

m  = Inspection(name="derp",method="lines", parameters={"angle":[0,90],"saveFile":"test12.png"}).execute(Image("./testdata/lines.png"))
result.append(m)

n  = Inspection(name="derp",method="lines", parameters={"length":[10,300],"saveFile":"test13.png"}).execute(Image("./testdata/lines.png"))
result.append(n)

print "Doing circles now..."

p  = Inspection(name="derp",method="circles",parameters={"saveFile":"test14.png"}).execute(Image("./testdata/circles.jpg"))
result.append(p)

q  = Inspection(name="derp",method="circles",parameters={"canny":200,"saveFile":"test15.png"}).execute(Image("./testdata/circles.jpg"))
result.append(q)

r  = Inspection(name="derp",method="circles",parameters={"saveFile":"test16.png","radius":[0,200]}).execute(Image("./testdata/circles.jpg"))
result.append(r)

s  = Inspection(name="derp",method="circles",parameters={"threshold":200,"saveFile":"test17.png"}).execute(Image("./testdata/circles.jpg"))
result.append(s)

print result

