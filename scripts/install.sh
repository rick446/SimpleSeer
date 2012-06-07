#!/bin/sh
#This is an install script for Seer.  It is intended to run on Ubuntu 12.04
#it is meant to run from where you want to run SimpleSeer from
sudo apt-get install python-dev python-setuptools python-pip libzmq-dev mongodb nodejs npm build-essential python-gevent libevent-dev supervisor ipython-notebook
sudo npm install -g brunch
sudo pip install -r pip.requirements
sudo python setup.py develop
sudo mkdir /etc/simpleseer
sudo ln -s `pwd`/SimpleSeer/static/ /etc/simpleseer/static
sudo ln -s `pwd`/etc/supervisor.conf /etc/supervisor/conf.d/supervisor.conf
sudo ln -s `pwd`/etc/simpleseer.cfg /etc/simpleseer.cfg
sudo ln -s `pwd`/etc/simpleseer-logging.cfg /etc/simpleseer-logging.cfg
sudo killall supervisord
sudo supervisord
sudo supervisorctl start seer-dev:
