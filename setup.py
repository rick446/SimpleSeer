from setuptools import setup, find_packages
import os, sys, glob, fnmatch

plugins_ini = os.path.join(
    os.path.dirname(__file__),
    'SimpleSeer/plugins/plugins.ini')
    
entry_points = '''
[seer.commands]
perftest = SimpleSeer.commands:PerfTestCommand
core = SimpleSeer.commands:CoreCommand
core-states = SimpleSeer.commands:CoreStatesCommand
broker = SimpleSeer.commands:BrokerCommand
web = SimpleSeer.commands:WebCommand
scrub = SimpleSeer.commands:ScrubCommand
shell = SimpleSeer.commands:ShellCommand
notebook = SimpleSeer.commands:NotebookCommand
controls = SimpleSeer.commands:ControlsCommand
replicate = SimpleSeer.commands:ReplicateCommand
script = SimpleSeer.commands:ScriptCommand
'''
entry_points += '''
[paste.paster_create_template]
simpleseer=SimpleSeer.template:SimpleSeerProjectTemplate
'''
with open(plugins_ini) as fp:
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
