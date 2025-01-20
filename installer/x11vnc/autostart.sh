#!/bin/sh
cd /root
dhclient &
pulseaudio &
python3 -m daas.runner_instance &


