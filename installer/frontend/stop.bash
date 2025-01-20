#!/bin/bash
FRONT_DIR=$(dirname "$0")/../../../../design-daas-application-frontend
cd "$FRONT_DIR/" || exit 1
docker-compose -f docker-compose-pve.yml down
