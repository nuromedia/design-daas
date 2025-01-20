#!/bin/bash

pulseaudio &
echo "remote-cursor: local" > /etc/guacamole/guacamole.properties
guacd -b 0.0.0.0 -L "$GUACD_LOG_LEVEL" -f &
tail -f /var/log/lastlog


