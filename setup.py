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
  scripts=['scripts/simpleseer', 'scripts/simpleseer-scrub'],
  data_files=[ ('/etc/',['etc/simpleseer.cfg']) ]
  )
