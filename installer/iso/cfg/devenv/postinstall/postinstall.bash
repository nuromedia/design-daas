#!/bin/bash

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

# systemd unit
cat <<EOF > /etc/systemd/system/firstboot.service
[Unit]
Description=Firstboot script
Before=getty@tty1.service
[Service]
Type=oneshot
ExecStart=/firstboot.bash
StandardInput=tty
StandardOutput=tty
StandardError=tty
[Install]
WantedBy=getty.target
EOF

# preseed-launcher
cat <<EOF > /firstboot.bash
#!/bin/bash
/opt/postinstall/postinstall_custom.bash
systemctl disable firstboot.service
rm -rf /etc/systemd/service/firstboot.service
rm -rf /firstboot.bash
exit 0
EOF

# enable service
chmod +x /firstboot.bash
systemctl enable firstboot.service

