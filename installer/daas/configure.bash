#!/bin/bash

# Configurable variables
export DEBIAN_FRONTEND=noninteractive

# help message
usage() { echo "Usage: $0 [-r <folder> -h <hostname> -d <domain> -i <ip-part>]" 1>&2; exit 1; }

# Read options
REPO_FOLDER=
HOST_NAME=
DOMAIN_NAME=
FRONT_NAME="front"
IP_PART=1
STANDALONE=
DEVICE_NAME=enp0s4
while getopts ":r:h:d:i:s:" o; do
    case "${o}" in
        r)
            REPO_FOLDER=${OPTARG}
            ;;
        h)
            HOST_NAME=${OPTARG}
            ;;
        d)
            DOMAIN_NAME=${OPTARG}
            ;;
        i)
            IP_PART=${OPTARG}
            ;;
        s)
            STANDALONE=${OPTARG}
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



# Configure
CFG_FOLDER="$REPO_FOLDER/src/config"
cd "$CFG_FOLDER" || exit 1
if [ "$STANDALONE" == "" ] ; then
    echo "STANDALONE=FALSE"
    sed -e "s#bridge_gw_daas = \"\"#bridge_gw_daas = \"192.168.123.1\"#g" -i vm.toml
    sed -e "s#bridge_adapter_daas = \"\"#bridge_adapter_daas = \"$DEVICE_NAME\"#g" -i vm.toml
else
    echo "STANDALONE=TRUE"
    sed -e "s#bridge_gw_daas = \"192.168.123.1\"#bridge_gw_daas = \"\"#g" -i vm.toml
    sed -e "s#bridge_adapter_daas = \"$DEVICE_NAME\"#bridge_adapter_daas = \"\"#g" -i vm.toml
    echo "dhclient for $DEVICE_NAME"
    dhclient "$DEVICE_NAME"
fi
sed -e "s#pve1.cluster.local#$HOST_NAME.$DOMAIN_NAME#g" -i qweb.toml
sed -e "s#pve1.cluster.local#$HOST_NAME.$DOMAIN_NAME#g" -i proxy.toml
sed -e "s#pve1.cluster.local#$HOST_NAME.$DOMAIN_NAME#g" -i vm.toml
sed -e "s#192.168.100.111/24#192.168.100.$IP_PART/24#g" -i vm.toml
sed -e "s#192.168.123.111/24#192.168.123.$IP_PART/24#g" -i vm.toml
sed -e "s#192.168.223.111/24#192.168.223.$IP_PART/24#g" -i vm.toml
sed -e "s#192.168.200.111/24#192.168.200.$IP_PART/24#g" -i vm.toml
sed -e "s#node = \"pve1\"#node = \"$HOST_NAME\"#g" -i vm.toml
sed -e "s#\"192.168.123.111\"#\"192.168.123.$IP_PART\"#g" -i vm.toml
sed -e "s#\"192.168.123.111\"#\"192.168.123.$IP_PART\"#g" -i container.toml
cd - || exit 1

cd "$REPO_FOLDER/installer/daas" || exit 1
mkdir -p /etc/nginx/ssl
CERTOPTS="/C=DE/ST=HE/L=FFM/O=PVE/OU=$HOST_NAME/CN=$HOST_NAME.$DOMAIN_NAME"
if [[ ! -f /etc/nginx/ssl/selfsigned.crt ]] ; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/selfsigned.key \
        -out /etc/nginx/ssl/selfsigned.crt \
        -subj "$CERTOPTS"
fi

cp daas.conf /etc/nginx/sites-available/daas.conf
cp nginx.conf /etc/nginx/nginx.conf
sed -i -e "s#pve1.cluster.local#$HOST_NAME.$DOMAIN_NAME#g" /etc/nginx/nginx.conf
sed -i -e "s#front1.cluster.local#$FRONT_NAME.$DOMAIN_NAME#g" /etc/nginx/nginx.conf
sed -i -e "s#pve1.cluster.local#$HOST_NAME.$DOMAIN_NAME#g" /etc/nginx/sites-available/daas.conf
rm -rf /etc/nginx/sites-enabled/daas.conf
ln -s /etc/nginx/sites-available/daas.conf /etc/nginx/sites-enabled/
systemctl restart nginx
cd - || exit 1

cd "$REPO_FOLDER" || exit 3
mkdir -p src/data
cp -r src/data_template/* src/data/
cd - || exit 1











