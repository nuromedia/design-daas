#!/bin/bash

# Configurable variables
SERVICE_NAME=frontend
export DEBIAN_FRONTEND=noninteractive

# help message
usage() { echo "Usage: $0 [-r <daas-repo> -f <frontend-repo> -h <hostname>]" 1>&2; exit 1; }

# Read options
REPO_FOLDER=/home/design-daas
FRONTEND_FOLDER=
HOST_NAME=
while getopts ":r:f:h:" o; do
    case "${o}" in
        r)
            REPO_FOLDER=${OPTARG}
            ;;
        f)
            FRONTEND_FOLDER=${OPTARG}
            ;;
        h)
            HOST_NAME=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Bail if requirements are not met
if [ -z "$REPO_FOLDER" ] ; then
    usage
fi
if [ -z "$FRONTEND_FOLDER" ] ; then
    usage
fi
if [ -z "$HOST_NAME" ] ; then
    usage
fi

# Extract ID from isoname
ID=0
[[ $HOST_NAME = *[1] ]] && ID=1
[[ $HOST_NAME = *[2] ]] && ID=2
[[ $HOST_NAME = *[3] ]] && ID=3

export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
rm -rf "$FRONTEND_FOLDER"
#git clone git@github.com:Nuromedia/design-daas-application-frontend.git "$FRONTEND_FOLDER"

NAME_TEST=`cat /etc/hosts | grep "front$ID" | wc -l`
if [[ $NAME_TEST -eq 0 ]] ; then
    echo "192.168.123.11$ID front$ID.cluster.local front$ID" >> /etc/hosts
    echo "Appended hostname 'front$ID.cluster.local+front$ID' in /etc/hosts"
fi
cd "$REPO_FOLDER/installer/frontend" || exit 1
cp frontend.conf /etc/nginx/sites-available/frontend.conf
sed -i -e "s#front1.cluster.local#front$ID.cluster.local#g" /etc/nginx/sites-available/frontend.conf
rm -rf /etc/nginx/sites-enabled/frontend.conf
ln -s /etc/nginx/sites-available/frontend.conf /etc/nginx/sites-enabled/
systemctl restart nginx
cd - || exit 1


