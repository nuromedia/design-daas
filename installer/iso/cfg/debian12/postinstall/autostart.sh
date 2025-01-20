#!/bin/bash
cd /root
function ncsocket() {

    while true; 
        do 
            nc -l -p "8080" | tee /dev/stdout | pacat --format=s16le --channels=1 --rate=44100 --device=virtual_speaker; 
        done 
}
pulseaudio &
dhclient &
ncsocket &
sleep 2
python3 -m daas.runner_instance &

