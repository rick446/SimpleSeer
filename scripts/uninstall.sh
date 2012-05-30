#!/bin/sh
sudo killall supervisord
sudo rm -f /usr/local/bin/simpleseer
sudo rm -rf /usr/local/lib/python2.7/dist-packages/SimpleSeer.egg-link
sudo rm -rf /etc/simpleseer
sudo rm -f /etc/supervisor/conf.d/supervisor.conf
sudo rm -f /etc/simpleseer.cfg
sudo rm -f /etc/simpleseer-logging.cfg
