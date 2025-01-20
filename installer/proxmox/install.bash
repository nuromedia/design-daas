#!/bin/bash

# Usage
usage() {
    echo "Usage: $0 [-i <ip-address>] [-h <hostname>] [-d <domain>]" 1>&2
    exit 1
}

# Default params (devenv)
PROXMOX_IP=
PROXMOX_HOST=
PROXMOX_DOMAIN=
PROXMOX_DEBURL=http://download.proxmox.com/debian/pve
PROXMOX_KEYURL=https://enterprise.proxmox.com/debian/proxmox-release-bookworm.gpg
export DEBIAN_FRONTEND=noninteractive

# Read options
while getopts ":i:h:d:" o; do
    case "$o" in
        i)
            PROXMOX_IP=${OPTARG}
            ;;
        h)
            PROXMOX_HOST=${OPTARG}
            ;;
        d)
            PROXMOX_DOMAIN=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Bail if requirements are not met
if  [ "$PROXMOX_IP" = "" ] || [ "$PROXMOX_HOST" = "" ] \
    || [ "$PROXMOX_DOMAIN" = "" ] ; then
    usage
fi

install_kernel() {
    sudo -E apt --yes update && sudo -E apt --yes install wget python3.11-venv
    # Sources
    echo "deb [arch=amd64] $PROXMOX_DEBURL bookworm pve-no-subscription" |
        sudo tee /etc/apt/sources.list.d/pve-install-repo.list
    sudo wget "$PROXMOX_KEYURL" \
        -O /etc/apt/trusted.gpg.d/proxmox-release-bookworm.gpg

    # Install kernel
    sudo -E apt --yes update && sudo -E apt --yes full-upgrade
    sudo -E apt --yes install pve-kernel-6.2
    [[ -f /etc/apt/sources.list.d/pve-enterprise.list ]] && \
        rm -rf /etc/apt/sources.list.d/pve-enterprise.list
}
install_pve() {
    sudo -E apt --yes install proxmox-ve open-iscsi
    sudo -E apt --yes remove linux-image-amd64 'linux-image-6.1*'
    sudo -E apt --yes remove os-prober
    sudo -E apt --yes install pip docker.io nginx build-essential python3.11-dev
    sudo -E pip install docker --break-system-packages
    sudo -E update-grub
    # Prepare docker daemon for default folder
    mkdir -p /etc/docker
    mkdir -p /home/daas-docker
    cat <<EOF > /etc/docker/daemon.json
{
    "data-root": "/home/daas-docker"
}
EOF
    systemctl restart docker
}
install_dnsmasq(){
    sudo -E apt --yes install python3-click dnsmasq
    cat <<EOF > /etc/dnsmasq.conf
server=8.8.8.8
interface=vmbr1
dhcp-range=192.168.223.50,192.168.223.75,1m
dhcp-option=vmbr1,3,$PROXMOX_IP
dhcp-option=vmbr1,6,8.8.8.8
dhcp-leasefile=/var/lib/misc/dnsmasq.leases
conf-dir=/etc/dnsmasq.d,.bak
EOF
    cat <<EOF > /etc/dnsmasq.d/pve-hosts.conf
dhcp-host=de:ad:be:ef:00:64,id:vm100,192.168.223.100,1m
dhcp-host=de:ad:be:ef:00:65,id:vm100,192.168.223.101,1m
dhcp-host=de:ad:be:ef:00:66,id:vm100,192.168.223.102,1m
dhcp-host=de:ad:be:ef:00:67,id:vm100,192.168.223.103,1m
dhcp-host=de:ad:be:ef:00:68,id:vm100,192.168.223.104,1m
EOF
    systemctl stop dnsmasq.service
    systemctl start dnsmasq.service
}
configure_hostname() {
    # Configure hostname
    cp /etc/hosts /etc/hosts.bak
    cp /etc/hostname /etc/hostname.bak
    hostname -b "$PROXMOX_HOST"
    echo "$PROXMOX_HOST" | sudo tee /etc/hostname
    cat <<EOF > /etc/hosts
127.0.0.1 localhost
$PROXMOX_IP $PROXMOX_HOST.$PROXMOX_DOMAIN $PROXMOX_HOST

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF
}
# Chose installation path
KERNEL=$(uname -r | grep pve)
if [[ "$KERNEL" == "" ]] ; then
    install_kernel
    configure_hostname
    #shutdown -r now
fi
if [[ "$KERNEL" != "" ]] ; then
    install_pve
    install_dnsmasq
fi
