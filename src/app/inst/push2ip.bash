#!/bin/bash

if [[ $# -ne 1 ]] ; then
    echo "Please give only an ip as argument!"
    echo "Exiting!"
    exit 1
fi

IP=$1
USER="root"
SRCFOLDER=/home/design-daas/backend/noweb
REMOTEFOLDER=daas/env
scp -r $SRCFOLDER/*.py "${USER}"@"${IP}":"$REMOTEFOLDER"
scp -r $SRCFOLDER/adapter/*.py "${USER}"@"${IP}":"$REMOTEFOLDER/adapter/"
scp -r $SRCFOLDER/adapter/tools/*.py "${USER}"@"${IP}":"$REMOTEFOLDER/adapter/tools"
