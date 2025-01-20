#!/bin/bash

# Usage
usage() {
    echo "Usage:"
    echo "$0 [-c <cluster to create> -j <cluster to join>] -l <link>"
    exit 1
}

# Default params (devenv)
CLUSTER_NAME=
CLUSTER_IP=
LINK_IP=
ACTION=

# Read options
while getopts ":c:i:l:" o; do
    case "${o}" in
        c)
            CLUSTER_NAME=${OPTARG}
            ACTION="create"
            ;;
        i)
            CLUSTER_IP=${OPTARG}
            ACTION="join"
            ;;
        l)
            LINK_IP=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Bail if requirements are not met
if  [ -z "$ACTION" ] ; then
    usage
fi
if  [ -z "$LINK_IP" ] ; then
    usage
fi
if [ "$ACTION" == "create" ] ; then
    if  [ -z "$CLUSTER_NAME" ] ; then
        usage
    fi
elif [ "$ACTION" == "join" ] ; then
    if  [ -z "$CLUSTER_IP" ] ; then
        usage
    fi
fi

cluster_create() {
    sudo pvecm create "$CLUSTER_NAME" --link0 "$LINK_IP"
}
cluster_join() {
    pvecm add "$CLUSTER_IP" --link0 "$LINK_IP"
}

if [ "$ACTION" == "create" ] ; then
    cluster_create
elif [ "$ACTION" == "join" ] ; then
    cluster_join
fi
