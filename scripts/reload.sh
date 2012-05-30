#!/bin/sh
#This script deletes and resets SimpleSeer
#please run this script from the main Seer directory
#>source scripts/reload.sh
sudo killall supervisord
sudo rm -f /usr/local/bin/simpleseer
sudo rm -rf /usr/local/lib/python2.7/dist-packages/SimpleSeer.egg-link
sudo rm -rf /etc/simpleseer
sudo rm -f /etc/supervisor/conf.d/supervisor.conf
sudo rm -f /etc/simpleseer.cfg
sudo rm -f /etc/simpleseer-logging.cfg
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
