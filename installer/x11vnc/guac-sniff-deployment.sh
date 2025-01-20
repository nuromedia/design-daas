#!/bin/bash
set -euo pipefail # strict mode

USAGE="$0 COMMAND

This script sets up a Guacamole deployment that can be used
for capturing the Guacamole protocol packets.

Commands:
  help       show this message and exit

  prepare    create or pull necessary container images
  start      start Guacamole containers
  stop       stop Guacamole containers
  status     show IP addresses of running Guacamole containers

  destination-start
  destination-stop
    start/stop the VNC server that can be connected to
"

PREFIX=guacsniff

PG_NAME=$PREFIX-database
GUACD_NAME=$PREFIX-guacd
PROXY_NAME=$PREFIX-proxy
NETWORK_NAME=$PREFIX-net

PG_IMAGE=docker.io/postgres
GUACD_IMAGE=docker.io/guacamole/guacd
PROXY_IMAGE=docker.io/guacamole/guacamole

PG_PASS=crossing-cropland-vaccine  # chosen by fair dice roll

DESTINATION_NAME=x11vnc
DESTINATION_IMAGE=x11vnc

warn() {
    echo "$@" >&2
}

# explicitly COMMAND...
#
# Log and run that command.
explicitly() {
    warn "running: $@"
    "$@"
}

command-prepare() {
    warn "preparing x11vnc container..."
    make build
    warn "preparing x11vnc container... done"

    warn
    warn "pulling relevant containers..."
    docker pull $GUACD_IMAGE
    docker pull $PROXY_IMAGE
    docker pull $PG_IMAGE
    warn "pulling relevant containers... done"
}

command-start() {
    warn
    warn "creating a network..."
    docker network create $NETWORK_NAME
    warn "creating a network... done"

    warn
    warn "setting up postgres database..."
    explicitly docker run --rm --name $PG_NAME --detach \
           --network $NETWORK_NAME \
           -e POSTGRES_USER=guacamole_user \
           -e POSTGRES_PASSWORD="$PG_PASS" \
           -e POSTGRES_DB=guacamole_db \
           $PG_IMAGE
    # wait for the DB to be ready
    while ! explicitly docker exec $PG_NAME \
                      pg_isready -d guacamole_db -U guacamole_user; do
        sleep 1
    done
    # run DB init script
    explicitly docker run --rm $PROXY_IMAGE /opt/guacamole/bin/initdb.sh --postgresql \
        | explicitly docker exec -i $PG_NAME \
                     psql -d guacamole_db -U guacamole_user -f -
    warn "setting up postgres database... done"

    warn
    warn "launching guacd..."
    explicitly docker run --rm --name $GUACD_NAME --detach \
           --network $NETWORK_NAME \
           $GUACD_IMAGE
    warn "launching guacd... done"

    warn "launching Guacamole proxy..."
    explicitly docker run --rm --name $PROXY_NAME --detach \
           --network $NETWORK_NAME \
           -e GUACD_HOSTNAME=$(docker-container-ip $GUACD_NAME) \
           -e POSTGRESQL_HOSTNAME=$(docker-container-ip $PG_NAME) \
           -e POSTGRESQL_USER=guacamole_user \
           -e POSTGRESQL_PASSWORD="$PG_PASS" \
           -e POSTGRESQL_DATABASE=guacamole_db \
           $PROXY_IMAGE
    warn "launching Guacamole proxy... done"
}

command-stop() {
    warn "shutting down all containers..."
    # is allowed to fail if those containers don't (yet) exist
    explicitly docker stop --time=5 $PG_NAME $GUACD_NAME $PROXY_NAME || true
    warn "shutting down all containers... done"

    warn "shutting down network..."
    explicitly docker network rm $NETWORK_NAME
    warn "shutting down network... done"
}

command-status() {
    for container in $PG_NAME $GUACD_NAME $PROXY_NAME $DESTINATION_NAME; do
        ip="$(docker-container-ip $container || true)"
        case "$ip" in
             "") echo "$container not running" ;;
             *) echo "$container running at IP $ip" ;;
        esac
    done
}

command-destination-start() {
	  explicitly docker run --rm --name $DESTINATION_NAME --detach \
               --network $NETWORK_NAME \
               $DESTINATION_IMAGE firefox google.com
}

command-destination-stop() {
    explicitly docker stop --time=5 $DESTINATION_NAME
}

# docker-container-ip CONTAINER
#
# Get the IP address of a running Docker container via "docker inspect"
docker-container-ip() {
    docker inspect \
           --format '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
           "$1"
}

command="${1-help}"
case "$command" in
    prepare)
        command-prepare
        ;;
    start)
        command-start
        ;;
    stop)
        command-stop
        ;;
    status)
        command-status
        ;;
    destination-start)
        command-destination-start
        ;;
    destination-stop)
        command-destination-stop
        ;;
    help)
        echo "$USAGE"
        exit
        ;;
    *)
        warn "unknown command `$command`"
        warn "$USAGE"
        exit 1
        ;;
esac
