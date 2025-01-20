#!/bin/bash

DAAS_DIR=$(dirname "$0")/../../src
cd "$DAAS_DIR/" || exit 1
PID=$(pgrep -f "python3 main.py")
if [[ $PID -gt 0 ]] ; then
    kill "$PID"
fi

