#!/bin/bash

service ssh start

export DISPLAY=:0
/usr/bin/Xtigervnc "$DISPLAY" -rfbport 5900 -localhost=0 -SecurityTypes VncAuth,TLSVnc \
    -PasswordFile tiger-vnc-password.txt \
    -BlacklistTimeout 1000 -BlacklistThreshold 10000 -FrameRate 60 \
    -geometry 1920x1080 -desktop localhost:0 -depth 32 -auth /root/.Xauthority &

function ncsocket() {

    while true; 
        do 
            nc -l -p "8080" | tee /dev/stdout | pacat --format=s16le --channels=1 --rate=44100 --device=virtual_speaker; 
        done 
}
pulseaudio &
ncsocket &
cupsd &
cd /root || exit 1
python3 -m daas.runner_instance &

CMD=$*
if [ "$CMD" == "" ] ; then
    CMD="xterm"
fi
DISPLAY=:0 xrdb -merge ~/.Xresources
DISPLAY=:0 qtile start
