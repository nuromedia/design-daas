#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
export TZ=Europe/Berlin
apt-get update -y && apt-get upgrade -y && apt-get install -y tzdata vim kitty
ln -snf /usr/share/zoneinfo/"$TZ" /etc/localtime && echo "$TZ" > /etc/timezone
apt-get install -y net-tools psmisc dnsutils netcat-traditional git make
apt-get install -y xorg galculator pulseeffects 
apt-get install -y python3 python3-click pip ceph-common ceph-fuse 
ln -s /usr/bin/python3 /usr/bin/python
pip install --break-system-packages psutil pika netifaces click \
    cairocffi dbus-next qtile

# SSH
if [[ -f /opt/postinstall/ssh/id_rsa.pub ]] ; then
    mkdir -p /root/.ssh
    cp /opt/postinstall/ssh/id_rsa* /root/.ssh/
    chmod 0700 /root/.ssh/id_rsa*
    cp /opt/postinstall/ssh/id_rsa.pub /root/.ssh/authorized_keys
fi
if [[ -f /opt/postinstall/ssh/sshd_config ]] ; then
    cp /opt/postinstall/ssh/sshd_config /etc/ssh/sshd_config
fi
systemctl disable ssh.service

# pulseaudio
PA_OPTS="auth-ip-acl=172.17.0.0/24 auth-anonymous=1"
echo "load-module module-native-protocol-tcp $PA_OPTS" >> /etc/pulse/default.pa
echo "load-module module-null-sink" >> /etc/pulse/default.pa
echo "load-module module-null-sink sink_name=\"virtual_speaker\" sink_properties=device.description=\"virtual_speaker\"" >> /etc/pulse/default.pa
echo "load-module module-remap-source master=\"virtual_speaker.monitor\" source_name=\"virtual_mic\"" >> /etc/pulse/default.pa
cat <<EOF > /etc/systemd/system/pulseaudio.service
[Unit]
Description=PulseAudio Sound Server

[Service]
Type=simple
ExecStart=/usr/bin/pulseaudio

[Install]
WantedBy=multi-user.target
EOF
systemctl disable pulseaudio.service

cat <<EOF > /etc/systemd/system/firstboot.service
[Unit]
Description=First Boot Setup
After=network.target

[Service]
Type=oneshot
ExecStart=/opt/postinstall/postinstall_firstboot.bash
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
systemctl enable firstboot.service
shutdown -r now
