#!/bin/bash

/usr/bin/Xtigervnc :0 -rfbport 5900 -localhost=0 -SecurityTypes VncAuth,TLSVnc \
    -PasswordFile tiger-vnc-password.txt \
    -geometry 1920x1080 -desktop localhost:0 -depth 32 -auth /root/.Xauthority &
service ssh start
pulseaudio &

CMD=$*
if [ "$CMD" == "" ] ; then
    CMD="xterm"
fi


DISPLAY=:0 xrandr --output VNC-0 --mode 1280x800
#DISPLAY=:0 firefox www.google.de
DISPLAY=:0 xrdb -merge ~/.Xresources

DISPLAY=:0 qtile start &


# lutris
chown wineuser:wineuser -R /home/wineuser
#sudo -u wineuser DISPLAY=:0 WINEARCH=win64 /usr/games/lutris &

# Run testapp
#DISPLAY=:0 wine /root/shared/.wine64/drive_c/app.exe &

# Init wine
#/wine-init.bash

tail -f /dev/null


