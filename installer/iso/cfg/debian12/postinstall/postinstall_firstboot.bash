#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
apt-get update -y && apt-get upgrade -y
apt-get install -y cups systemd-timesyncd pulseaudio lightdm

# qtile
mkdir -p /root/.config/qtile
cp /opt/postinstall/config.py /root/.config/qtile/config.py
cp /opt/postinstall/qtile.desktop /usr/share/xsessions/qtile.desktop
cp /opt/postinstall/autostart.sh /root/.config/qtile/autostart.sh
chmod a+x /root/.config/qtile/autostart.sh

# daas
echo "export DISPLAY=:0" >> /root/.bashrc
echo "xhost + >/dev/null" >> /root/.bashrc
mkdir -p /root/daas/env
mkdir -p /root/daas/status
cp -r /opt/postinstall/daas/* /root/daas/
cp -r /opt/postinstall/daas.jpg /root/daas/env/daas.jpg

echo "[Seat:*]" > /etc/lightdm/lightdm.conf
echo "autologin-user=root" >> /etc/lightdm/lightdm.conf
echo "autologin-session=qtile" >> /etc/lightdm/lightdm.conf
sudo sed -e '/pam_succeed_if.so/ s/^#*/#/' -i /etc/pam.d/lightdm-autologin

# Remove firstboot 
systemctl enable systemd-timesyncd
systemctl enable cups
systemctl enable lightdm
systemctl enable ssh
rm -rf /etc/systemd/system/firstboot.service
shutdown -r now

