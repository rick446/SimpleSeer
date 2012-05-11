#!/bin/bash

SCRIPT=`readlink -f $0`
DIR=`dirname $SCRIPT`
DIR="${DIR}/../SimpleSeer/static"

cd $DIR
brunch watch
 

