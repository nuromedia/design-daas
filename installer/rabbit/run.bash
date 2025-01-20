#!/bin/bash

HOSTNAME=daas-0-rabbit
HOSTIP=172.17.0.1
CONTAINERNAME=daas-0-rabbit
docker run --rm -d --hostname "$HOSTNAME" --name "$CONTAINERNAME" \
    -p "$HOSTIP":4369:4369 -p "$HOSTIP":5672:5672 \
    rabbitmq:3
