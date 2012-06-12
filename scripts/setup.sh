#!/bin/sh
#This is a setup tool to help automate the installation of SimpleSeer
#Please run this from the top level seer directory
#so for instance if you are running in /tmp/SimpleSeer than
# cd /tmp/SimpleSeer
# source scripts/setup.sh
#
#

seer_install () {
  echo "[Installing Seer]"
  echo "installing required system libraries"
  sudo apt-get install python-dev python-setuptools python-pip libzmq-dev nodejs npm build-essential python-gevent libevent-dev supervisor ipython-notebook
  echo "installing brunch"
  sudo npm install -g brunch
  echo "installing PIP requirements"
  sudo pip install -r pip.requirements
  echo "linking for development"
  sudo python setup.py develop
  echo "setting up environment"
  sudo mkdir /etc/simpleseer
  sudo ln -s `pwd`/SimpleSeer/static/ /etc/simpleseer/static
  sudo ln -s `pwd`/etc/supervisor.conf /etc/supervisor/conf.d/supervisor.conf
  sudo ln -s `pwd`/etc/simpleseer.cfg /etc/simpleseer.cfg
  sudo ln -s `pwd`/etc/simpleseer-logging.cfg /etc/simpleseer-logging.cfg
  echo "stopping supervisord"
  sudo supervisorctl stop all
  sudo killall supervisord
  echo "starting supervisord"
  sudo supervisord
  echo "starting all SimpleSeer services"
  sudo supervisorctl start seer-dev:
  echo ""
  echo ""
  echo "Everything should now be installed and working, test at:"
  echo "http://localhost:8080"
  echo ""
  echo "if not please consult simpleseer.XXYYZZ.log in /tmp/ to determine issue"
  echo ""
  echo ""
}

seer_delete () {
  echo "[Deleting Seer]"
  echo "stopping supervisord"
  sudo supervisorctl stop all
  sudo killall supervisord
  echo "cleaning up old files..."
  sudo rm -f /usr/local/bin/simpleseer
  sudo rm -rf /usr/local/lib/python2.7/dist-packages/SimpleSeer.egg-link
  sudo rm -rf /etc/simpleseer
  sudo rm -f /etc/supervisor/conf.d/supervisor.conf
  sudo rm -f /etc/simpleseer.cfg
  sudo rm -f /etc/simpleseer-logging.cfg
  echo "...done deleting seer"
  echo ""
}

seer_reload () {
  echo "--------------"
  echo "Reloading Seer"
  echo "--------------"
  seer_delete
  echo "Please wait while sockets are closed..."
  sleep 15
  seer_install
}

mongo_install () {
  echo "[Installing Mongo]"
  echo ""
  echo "setting up directories"
  mkdir -p /tmp/mongo
  echo "downloading..."
  wget http://fastdl.mongodb.org/linux/mongodb-linux-x86_64-2.1.1.tgz -O /tmp/mongodb-linux-x86_64-2.1.1.tgz
  sudo tar zxvf /tmp/mongodb-linux-x86_64-2.1.1.tgz -C /tmp/mongo
  echo "copying files...."
  sudo cp /tmp/mongo/mongodb-linux-x86_64-2.1.1/bin/* /usr/local/bin/
  sudo mkdir -p /var/lib/mongodb
  sudo mkdir -p /var/log/mongodb
  sudo cp `pwd`/etc/mongodb.conf /etc/
  echo "...done installing mongo"
  echo ""
}

mongo_uninstall () {
  echo "[Removing Mongo]"
  sudo apt-get -f -y --force-yes remove mongodb
  sudo rm -f /usr/local/bin/bsondump
  sudo rm -f /usr/local/bin/mongod
  sudo rm -f /usr/local/bin/mongoexport
  sudo rm -f /usr/local/bin/mongoimport
  sudo rm -f /usr/local/bin/mongoperf
  sudo rm -f /usr/local/bin/mongos
  sudo rm -f /usr/local/bin/mongotop
  sudo rm -f /usr/local/bin/mongo
  sudo rm -f /usr/local/bin/mongodump
  sudo rm -f /usr/local/bin/mongofiles
  sudo rm -f /usr/local/bin/mongooplog
  sudo rm -f /usr/local/bin/mongorestore
  sudo rm -f /usr/local/bin/mongostat
  sudo rm -f /usr/local/bin/perftest
  sudo rm -rf /var/lib/mongodb
  sudo rm -rf /var/log/mongodb
  echo "...done removing mongo"
  echo ""
}



echo ""
echo ""
echo "+++++++++++++++++++++++++++++++++++++++++++++++"
echo "SimpleSeer setup tool"
echo "+++++++++++++++++++++++++++++++++++++++++++++++"
echo "*run this from the main SimpleSeer directory with:"
echo "source scripts/setup.sh"
echo ""
while true; do

    echo "-------------------------------------------------------------------------"
    read -p "[i]nstall, [r]eload, [d]elete, [m]ongo install, [k]ill mongo, or e[x]it this program?" choice
    case $choice in
        [i]* ) seer_install; break;;
        [r]* ) seer_reload; break;;
        [d]* ) seer_delete;;
        [m]* ) mongo_install;;
        [k]* ) mongo_uninstall;;
        [x]* ) echo "exiting...";break;;
        * ) echo "Please answer yes or no.";;
    esac
done
