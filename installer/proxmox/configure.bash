#!/bin/bash

usage() { echo "Usage: $0 [-r <folder>] [-h <hostname>]" 1>&2; exit 1; }

# Read options
REPO_FOLDER=
HOST_NAME=
HOST_DOMAIN=
IP_PART=11
while getopts ":r:h:i:d:" o; do
    case "${o}" in
        r)
            REPO_FOLDER=${OPTARG}
            ;;
        h)
            HOST_NAME=${OPTARG}
            ;;
        d)
            HOST_DOMAIN=${OPTARG}
            ;;
        i)
            IP_PART=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Bail if requirements are not met
if [ ! -d "$REPO_FOLDER" ] ; then
    usage
fi
if [ -z "$HOST_NAME" ] ; then
    usage
fi
exit 0

