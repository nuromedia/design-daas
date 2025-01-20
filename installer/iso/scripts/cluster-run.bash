#!/bin/bash

ISOFOLDER=iso
ISONAME=
VMSSHPORT=5555
QCOWSIZE=400
QCOWSIZE2=128
MEMSIZE=16382
GATEWAY_DEV=enp6s0
GATEWAY_BRIDGE=brdaas

export DEBIAN_FRONTEND=noninteractive


usage() {
    echo "Usage: $0 " 1>&2
    echo "      [-a <action>] [-n <isoname>]" 1>&2
    echo "      [-p <sshport>] [-s <disksize>]" 1>&2
    echo "      " 1>&2
    echo "      Action  : [wait,connect]" 1>&2
    echo "      Isoname : [isoname in ./iso without extension]" 1>&2
    echo "      Sshport : [ssh port (Default: 5555)]" 1>&2
    echo "      Disksize: [Size of disk in GB (Default: 128)]" 1>&2
}

while getopts ":a:e:h:n:p:s:" o; do
    case "$o" in
        a)
            ACTION=${OPTARG}
            ;;
        e)
            EXTRAPORTS=${OPTARG}
            ;;
        n)
            ISONAME=${OPTARG}
            ;;
        p)
            VMSSHPORT=${OPTARG}
            ;;
        s)
            QCOWSIZE=${OPTARG}
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

# Extract ID from isoname
ID=0
[[ $ISONAME = *[1] ]] && ID=1
[[ $ISONAME = *[2] ]] && ID=2
[[ $ISONAME = *[3] ]] && ID=3

PIDFILE="$ISOFOLDER"/pve"$ID".pid

kvminstall() {
    #sudo -E apt --yes install qemu-kvm
    echo "Nothing to install"
}

vmdisk(){
    rm -rf iso/cluster-"$ISONAME"-1.qcow2
    rm -rf iso/cluster-"$ISONAME"-2.qcow2
    qemu-img create -q -f qcow2 -o cluster_size=2M iso/cluster-"$ISONAME"-1.qcow2 "$QCOWSIZE"G
    # cp iso/cluster-temp/cluster-"$ISONAME"-1.qcow2 iso/cluster-"$ISONAME"-1.qcow2
    qemu-img create -q -f qcow2 -o cluster_size=2M iso/cluster-"$ISONAME"-2.qcow2 "$QCOWSIZE2"G
    # cp iso/cluster-temp/cluster-"$ISONAME"-2.qcow2 iso/cluster-"$ISONAME"-2.qcow2
}

vmstart() {
    sudo tunctl -t tapcls-"$ISONAME"
    sudo tunctl -t tapceph-"$ISONAME"
    sudo tunctl -t tapdaas-"$ISONAME"
    sudo tunctl -t tapinst-"$ISONAME"
    sudo brctl addif brcluster tapcls-"$ISONAME"
    sudo brctl addif brceph tapceph-"$ISONAME"
    sudo brctl addif brdaas tapdaas-"$ISONAME"
    sudo brctl addif brinst tapinst-"$ISONAME"
    sudo ifconfig tapcls-"$ISONAME" 0.0.0.0 up
    sudo ifconfig tapceph-"$ISONAME" 0.0.0.0 up
    sudo ifconfig tapdaas-"$ISONAME" 0.0.0.0 up
    sudo ifconfig tapinst-"$ISONAME" 0.0.0.0 up


    sudo kvm \
        -enable-kvm  \
        -machine q35,accel=kvm,usb=off,vmport=off,smm=on,dump-guest-core=off \
        -cpu host -smp 8,sockets=2,cores=4,threads=1 -m "$MEMSIZE" \
        -rtc 'clock=host,base=utc' \
        -boot strict=on \
        -parallel none -serial none -k de \
        -device virtio-balloon \
        -device usb-ehci -device usb-tablet \
        -object iothread,id=io0 \
        -pidfile "$PIDFILE" \
        -netdev tap,id=daasnet,ifname=tapdaas-"$ISONAME",script=no,downscript=no \
        -device e1000,netdev=daasnet,mac=52:55:00:d1:55:0"$ID" \
        -netdev tap,id=instnet,ifname=tapinst-"$ISONAME",script=no,downscript=no \
        -device e1000,netdev=instnet,mac=52:55:00:d1:55:1"$ID" \
        -netdev tap,id=cephnet,ifname=tapceph-"$ISONAME",script=no,downscript=no \
        -device e1000,netdev=cephnet,mac=52:55:00:d1:55:2"$ID" \
        -netdev tap,id=clusternet,ifname=tapcls-"$ISONAME",script=no,downscript=no \
        -device e1000,netdev=clusternet,mac=52:55:00:d1:55:3"$ID" \
        -object rng-random,id=rng0,filename=/dev/urandom \
        -device virtio-rng-pci,rng=rng0 \
        -object iothread,id=io1 \
        -drive if=none,id=disk0,format=qcow2,cache-size=16M,cache=none,file=iso/cluster-"$ISONAME"-1.qcow2 \
        -device virtio-blk-pci,drive=disk0,scsi=off,iothread=io1 \
        -drive if=none,id=disk1,format=qcow2,cache-size=16M,cache=none,file=iso/cluster-"$ISONAME"-2.qcow2 \
        -device virtio-blk-pci,drive=disk1,scsi=off,iothread=io1 \
        -cdrom "$ISOFOLDER/devenv-daas.iso" &
}
vmstop() {
    if [ -f "$PIDFILE" ] ; then
        sudo brctl delif brcluster tapcls-"$ISONAME"
        sudo brctl delif brceph tapceph-"$ISONAME"
        sudo brctl delif brdaas tapdaas-"$ISONAME"
        sudo brctl delif brinst tapinst-"$ISONAME"
        sudo ifconfig tapcls-"$ISONAME" down
        sudo ifconfig tapceph-"$ISONAME" down
        sudo ifconfig tapdaas-"$ISONAME" down
        sudo ifconfig tapinst-"$ISONAME" down
        PID=$(sudo cat "$PIDFILE")
        sudo kill "$PID"
        sudo rm -rf "$PIDFILE"
    fi
}

netstart() {
    sudo brctl addbr brceph
    sudo brctl addbr brdaas
    sudo brctl addbr brcluster
    sudo brctl addbr brinst
    sudo ifconfig brceph 192.168.100.1 up
    sudo ifconfig brdaas 192.168.123.1 up
    sudo ifconfig brcluster 192.168.200.1 up
    sudo ifconfig brinst 192.168.223.1 up
    sudo cp cfg/devenv/cluster/dnsmasq.conf /etc/dnsmasq.conf
    sudo service dnsmasq start
    # TODO: Replace by more restrict ruleset! (DEV-CONFIG)
    sudo sysctl -w net.ipv4.ip_forward=1
    sudo iptables -A FORWARD -i "$GATEWAY_BRIDGE" -o "$GATEWAY_DEV" -j ACCEPT
    sudo iptables -A FORWARD -o "$GATEWAY_BRIDGE" -i "$GATEWAY_DEV" -m state --state RELATED,ESTABLISHED -j ACCEPT
    sudo iptables -t nat -A POSTROUTING -o "$GATEWAY_DEV" -j MASQUERADE
}

netstop() {
    sudo ifconfig brceph down
    sudo ifconfig brdaas down
    sudo ifconfig brcluster down
    sudo ifconfig brinst down
    sudo brctl delbr brceph
    sudo brctl delbr brdaas
    sudo brctl delbr brcluster
    sudo brctl delbr brinst
    sudo service dnsmasq stop
    # TODO: Replace by more restrict ruleset! (DEV-CONFIG)
    sudo sysctl -w net.ipv4.ip_forward=0
    sudo iptables -D FORWARD -i "$GATEWAY_BRIDGE" -o "$GATEWAY_DEV" -j ACCEPT
    sudo iptables -D FORWARD -o "$GATEWAY_BRIDGE" -i "$GATEWAY_DEV" -m state --state RELATED,ESTABLISHED -j ACCEPT
    sudo iptables -t nat -D POSTROUTING -o "$GATEWAY_DEV" -j MASQUERADE
}

case "$ACTION" in
    "netstart")
        netstart
        ;;
    "netstop")
        netstop
        ;;
    "start")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        vmstart
        ;;
    "stop")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        vmstop
        ;;
    "install")
        kvminstall
        ;;
    "disk")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        vmdisk
        ;;
     *)
        echo "Not a valid target: '$1'"
        ;;
esac

