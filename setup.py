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
  barcode=SimpleSeer.plugins.barcode:Barcode
  blob=SimpleSeer.plugins.blob:Blob
  lines=SimpleSeer.plugins.lines:Lines  
  motion=SimpleSeer.plugins.motion:Motion
  region=SimpleSeer.plugins.region:Region
  face=SimpleSeer.plugins.face:Face
  circles=SimpleSeer.plugins.circles:Circles
  edgeWidth=SimpleSeer.plugins.edgeWidth:EdgeWidth
  simpleTemplate=SimpleSeer.plugins.simpleTemplate:SimpleTemplate

  [seer.plugins.measurement]
  blob_length=SimpleSeer.plugins.blob:BlobLength
  blob_count=SimpleSeer.plugins.blob:BlobCount

  [seer.plugins.watcher]
  smsalert=SimpleSeer.plugins.smsalert:SMSAlert
  ''')
