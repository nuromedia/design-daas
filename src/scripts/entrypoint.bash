#!/bin/bash

cd /opt/qweb || exit 123
source .venv/bin/activate
python3 main.py
