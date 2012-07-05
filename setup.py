from setuptools import setup, find_packages
import os, sys, glob, fnmatch

#from SimpleCV import __version__

entry_points = '''
[paste.paster_create_template]
simpleseer=SimpleSeer.template:SimpleSeerProjectTemplate
'''
with open("./SimpleSeer/plugins/plugins.ini") as fp:
    entry_points += fp.read()

setup(name="SimpleSeer",
  version=0.0,
  download_url='',
  description='',
  long_description='',
  classifiers=[ ],
  keywords='',
  author='Sight Machine',
  author_email='support@sightmachine.com',
  url='',
  license='BSD',
  packages = find_packages(exclude=['ez_setup']),
  zip_safe = False,
  requires=[],
  package_data  = { },
  scripts=['scripts/simpleseer'],
  data_files=[ ('/etc/',['etc/simpleseer.cfg']) ],
  entry_points=entry_points)
