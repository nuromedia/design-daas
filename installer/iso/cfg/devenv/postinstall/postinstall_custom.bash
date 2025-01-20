#!/bin/bash

export DEBIAN_FRONTEND=noninteractive
apt --yes install git sudo vim make
nslookup github.com

echo "Cloning design-daas repo..."
cd /home || exit 1
rm -rf design-daas
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
git clone git@github.com:Nuromedia/design-daas.git
mkdir -p /home/design-daas/backend/installer/iso/iso
sync

# echo "Cloning mps repo..."
# cd /opt || exit 2
# rm -rf mps
# export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
# git clone https://github.com/odem/mps.git
# cd /opt/mps || exit 3
# ./bootstrap.bash -u mps -p mps
# ./terminal.bash -u mps
# sync

# Final message
sleep 5
exit 0
