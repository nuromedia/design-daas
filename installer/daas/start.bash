#!/bin/bash

DAAS_DIR=$(dirname "$0")/../../src
cd "$DAAS_DIR/" || exit 1
make

