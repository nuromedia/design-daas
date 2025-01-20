#!/bin/bash

TIMEOUTS=1000
FQDN=localhost
VMSSHPORT=5555
USERNAME=root
INCFOLDER=config
export DEBIAN_FRONTEND=noninteractive

usage() {
    echo "Usage: $0 " 1>&2
    echo "      [-a <action>] [-n <isoname>]" 1>&2
    echo "      [-f <fqdn>] [-t <timeouts>]" 1>&2
    echo "      [-p <sshport>] [-u <sshuser>]" 1>&2
    echo "      [-i <incfolder>] " 1>&2
    echo "      " 1>&2
    echo "      Action  : [wait,connect]" 1>&2
    echo "      Isoname : [isoname in ./iso without extension]" 1>&2
    echo "      FQDN    : [Hostname to connect to (Default: localhost)]" 1>&2
    echo "      Sshuser : [ssh user (Default: root)]" 1>&2
    echo "      Sshport : [ssh port (Default: 5555)]" 1>&2
    echo "      Timeouts: [Wait attempts (Default: 1000)]" 1>&2
    echo "      IncDir  : [The include folder with key (Default: config)]" 1>&2
}

while getopts ":a:f:i:h:n:p:t:u:" o; do
    case "${o}" in
        a)
            ACTION=${OPTARG}
            ;;
        f)
            FQDN=${OPTARG}
            ;;
        i)
            INCFOLDER=${OPTARG}
            ;;
        n)
            ISONAME=${OPTARG}
            ;;
        p)
            VMSSHPORT=${OPTARG}
            ;;
        t)
            TIMEOUTS=${OPTARG}
            ;;
        u)
            USERNAME=${OPTARG}
            ;;
        h)
            usage && exit 0
            ;;
        *)
            usage && exit 1
            ;;
    esac
done
shift $((OPTIND-1))

SSHKEY=$INCFOLDER/ssh/id_rsa

OPTBATCH="-o BatchMode=yes -o ConnectTimeout=1"
OPTSTRICT="-o StrictHostKeyChecking=no -o NoHostAuthenticationForLocalhost=yes"
OPTAUTH="-i $SSHKEY -p $VMSSHPORT"
OPTHOST="$USERNAME@$FQDN"
OPTCMD="cd .."
SSHCMD="ssh $OPTSTRICT $OPTAUTH"
SSHCMD_TEST="$SSHCMD $OPTBATCH $OPTHOST $OPTCMD"
SSHCMD_BASH="$SSHCMD $OPTBATCH $OPTHOST"

vmwait() {
    echo -n "Waiting for ssh-connect "

    number=1 ; RET=-1 ; while [[ $number -le $TIMEOUTS ]] ; do
        $SSHCMD_TEST 2>/dev/null
        RET=$?
        if [[ $RET -eq 0 ]] ; then
            break
        else
            echo -n "."
            ((number = number + 1))
            sleep 1
        fi
    done
    [[ $RET -gt 0 ]] && echo " No success!" && exit 1
    [[ $RET -eq 0 ]] && echo " Done!"
    return $RET
}

vmconnect() {
    vmwait
    RET=$?
    if [[ $RET -eq 0 ]] ; then
        echo "$SSHCMD_BASH"
        $SSHCMD_BASH
    fi
}

case "$ACTION" in
    "wait")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        vmwait 1>&2 <>/dev/null
        ;;
    "connect")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        vmconnect
        ;;
     *)
        echo "Not a valid target: '$1'"
        ;;
esac

