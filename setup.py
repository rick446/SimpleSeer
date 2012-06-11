from setuptools import setup, find_packages
import os, sys, glob, fnmatch

#from SimpleCV import __version__

setup(name="SimpleSeer",
  version=0.0,
  download_url='',
  description='',
  long_description='',
  classifiers=[ ],
  keywords='',
  author='Ingenuitas Inc',
  author_email='support@ingenuitas.com',
  url='',
  license='BSD',
  packages = find_packages(exclude=['ez_setup']),
  zip_safe = False,
  requires=[],
  package_data  = { },
  scripts=['scripts/simpleseer'],
  data_files=[ ('/etc/',['etc/simpleseer.cfg']) ],
  entry_points='''
  [seer.plugins.inspection]
  barcode=SimpleSeer.plugins.Barcode:Barcode
  blob=SimpleSeer.plugins.Blob:Blob
  lines=SimpleSeer.plugins.Lines:Lines  
  motion=SimpleSeer.plugins.Motion:Motion
  region=SimpleSeer.plugins.Region:Region
  face=SimpleSeer.plugins.Face:Face
  circles=SimpleSeer.plugins.Circles:Circles
  edgeWidth=SimpleSeer.plugins.EdgeWidth:EdgeWidth
  simpleTemplate=SimpleSeer.plugins.SimpleTemplate:SimpleTemplate
  keypointTemplate=SimpleSeer.plugins.KeypointTemplate:KeypointTemplate
  ocr=SimpleSeer.plugins.OCR:OCR

  [seer.plugins.measurement]
  blob_length=SimpleSeer.plugins.Blob:BlobLength
  blob_count=SimpleSeer.plugins.Blob:BlobCount
  closestcolor=SimpleSeer.plugins.closestcolor:ClosestColorMeasurement
  timebetween=SimpleSeer.plugins.timebetween:TimeBetweenMeasurement

  [seer.plugins.watcher]
  smsalert=SimpleSeer.plugins.smsalert:SMSAlert
  ''')
