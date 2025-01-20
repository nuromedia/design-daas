#!/bin/bash

# Usage
usage() {
    echo "Usage: $0 [-n <ceph cidr>]" 1>&2
    exit 1
}

# Default params (devenv)
CEPH_NETWORK=
CEPH_DISK="/dev/vdb"
POOL_NAME=daas-ceph
FS_PUBNAME=pubfs
FS_SHAREDNAME=sharedfs
FS_USERNAME=userfs
FS_DAASNAME=daasfs

ACTION="install"
# Read options
while getopts ":a:n:d:" o; do
    case "${o}" in
        a)
            ACTION=${OPTARG}
            ;;
        d)
            CEPH_DISK=${OPTARG}
            ;;
        n)
            CEPH_NETWORK=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Bail if requirements are not met
if  [ -z "$CEPH_NETWORK" ] ; then
    usage
fi
if  [ -z "$ACTION" ] ; then
    usage
fi

install_ceph() {
    echo "yJ" | sudo pveceph install -repository no-subscription -version quincy
}
init_network() {
    sudo pveceph init --network "$CEPH_NETWORK"
}
create_monitor() {
    sudo pveceph mon create
}
create_manager() {
    sudo pveceph mgr create
}
create_osd() {
    sudo pveceph osd create "$CEPH_DISK"
}
create_mds() {
    pveceph mds
}
create_pool() {
    sudo pveceph pool create "$POOL_NAME" -pg_num 8 --add_storages
}

# create_cephfs_public() {
#     pveceph mds create --name $FS_PUBNAME
#     pveceph fs create -name $FS_PUBNAME -add-storage 0  -pg_num 8
# }
# create_cephfs_shared() {
#     pveceph mds create --name $FS_SHAREDNAME
#     pveceph fs create -name $FS_SHAREDNAME -add-storage 0  -pg_num 8
# }
# create_cephfs_user() {
#     pveceph mds create --name $FS_USERNAME
#     pveceph fs create -name $FS_USERNAME -add-storage 0  -pg_num 8
# }
create_cephfs_daas() {
    pveceph mds create --name "$FS_DAASNAME"
    pveceph mds create --name "${FS_DAASNAME}-standby"
    pveceph fs create -name $FS_DAASNAME -add-storage 0  -pg_num 16
}

action_ceph() {
    install_ceph
    init_network
    create_monitor
    create_manager
    #create_osd
    #create_mds
}
action_pool() {
    create_pool
}
action_cephfs() {
    create_cephfs_daas
}

if [ "$ACTION" == "ceph" ] ; then
    action_ceph
elif [ "$ACTION" == "cephfs" ] ; then
    action_cephfs
elif [ "$ACTION" == "pool" ] ; then
    action_pool
elif [ "$ACTION" == "osd" ] ; then
    create_osd
fi


