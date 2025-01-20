#!/bin/bash

# Configurable variables
SERVICE_NAME=daas
export DEBIAN_FRONTEND=noninteractive

# help message
usage() { echo "Usage: $0 [-r <folder>]" 1>&2; exit 1; }

# Read options
REPO_FOLDER=
while getopts ":r:" o; do
    case "${o}" in
        r)
            REPO_FOLDER=${OPTARG}
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
REPO_FOLDER=${REPO_FOLDER%/} # Remove trailing slash
cd "$REPO_FOLDER/src" || exit 1
make install

apt install -y nginx
 curl -SL \
     https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 \
     -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose
apt --yes install jq


# systemd unit
cat <<EOF > /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=daas starter
Before=getty@tty1.service
Wants=pve-cluster.service
Wants=pvedaemon.service
Wants=ssh.service
Wants=nginx.service
Wants=docker.service
Wants=pve-storage.target
After=pve-storage.target
After=pve-cluster.service
After=pvedaemon.service
After=ssh.service
After=nginx.service
After=network.target
After=docker.service
Requires=nginx.service
Requires=pveproxy.service
Requires=docker.service

[Service]
Type=simple
ExecStart=$REPO_FOLDER/installer/$SERVICE_NAME/start.bash
ExecStop=$REPO_FOLDER/installer/$SERVICE_NAME/stop.bash
[Install]
WantedBy=getty.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE_NAME.service
systemctl start $SERVICE_NAME.service
systemctl enable nginx
systemctl restart nginx
systemctl enable dnsmasq
systemctl restart dnsmasq

