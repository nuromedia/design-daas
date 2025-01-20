# default targets
.PHONY: default all install configure other \
	proxmox-all proxmox-install proxmox-install-pool \
	proxmox-install-cephfs proxmox-install-ceph \
	proxmox-configure proxmox-isogen proxmox-isoupload \
	proxmox-cluster-create proxmox-cluster-join \
	guacamole-all guacamole-install guacamole-configure \
	daas-all daas-install daas-configure daas-containers \
	frontend-all frontend-install frontend-configure \
	start stop

SERVICES := frontend.service daas.service guacamole.service pve-firewall.service \
			pvedaemon.service pve-ha-crm.service pve-ha-lrm.service \
			pve-lxc-syscalld.service pvefw-logger.service pveproxy.service \
			pvescheduler.service pvestatd.service spiceproxy.service

default: usage

# Makefile setup
SHELL:=/bin/bash

# Static config
DESIGN_BASE:=..
DESIGN_FOLDER:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))/$(DESIGN_BASE)
FRONTEND_FOLDER:=$(DESIGN_FOLDER)/../design-daas-application-frontend
PY3CMD:=cd $(DESIGN_FOLDER) && python3 -m backend.noweb.cmdline
ISODIR:=installer/iso/iso

# User Config
HOST_NUMBER?=11
HOST_IP?=10.0.2.15
HOST_NAME?=pve1
HOST_DOMAIN?=daas-design.de
CEPH_DISK?=/dev/vdb
CEPH_NETWORK?=192.168.100.0/24
CLUSTER_NAME?=clustertest
CLUSTER_IP?=192.168.200.11
STANDALONE?=""
LINK_IP?=

# Help
usage:
	@echo ""
	@echo "Usage: make TARGETS"
	@echo ""
	@echo "   COMMON: "
	@echo "     all                    : Invoke all targets"
	@echo "     install                : Invoke all install targets"
	@echo "     configure              : Invoke all configure targets"
	@echo "     other                  : Invoke all other targets"
	@echo ""
	@echo "   PROXMOX: "
	@echo "     proxmox-default        : Invokes default proxmox targets"
	@echo "     proxmox-install        : Invokes proxmox installer script"
	@echo "     proxmox-install-ceph   : Invokes proxmox ceph installation"
	@echo "     proxmox-install-osd    : Invokes proxmox osd create"
	@echo "     proxmox-install-cephfs : Invokes proxmox cephfs installation"
	@echo "     proxmox-install-pool   : Invokes proxmox ceph installation"
	@echo "     proxmox-cluster-create : Invokes proxmox ceph installer script"
	@echo "     proxmox-cluster-join   : Invokes proxmox ceph installer script"
	@echo "     proxmox-configure      : Invokes proxmox configure script"
	@echo "     proxmox-isogen         : Invokes iso installer"
	@echo ""
	@echo "   GUACAMOLE: "
	@echo "     guacamole-all          : Invokes all guacamole targets"
	@echo "     guacamole-install      : Invokes guacamole installer script"
	@echo "     guacamole-configure    : Invokes guacamole configure script"
	@echo ""
	@echo "   DAAS: "
	@echo "     daas-all               : Invokes daas targets"
	@echo "     daas-install           : Invokes daas installer script"
	@echo "     daas-configure         : Invokes daas configure script"
	@echo "     daas-containers        : Invokes daas container build"
	@echo "     daas-services          : Invokes daas services build"
	@echo ""
	@echo "   FRONTEND: "
	@echo "     frontend-all           : Invokes all frontend targets"
	@echo "     frontend-install       : Invokes frontend installer script"
	@echo "     frontend-configure     : Invokes frontend configure script"
	@echo ""
	@echo "   CONTROL: "
	@echo "     start             : Starts all services"
	@echo "     stop              : Stops all services"
	@echo ""
	@echo "   VARS: "
	@echo "     HOST_NUMBER            : Number added as ip prefix (Default: 11)"
	@echo "     HOST_IP                : The ip of the host system (Default: 10.0.2.15)"
	@echo "     HOST_NAME              : The hostname of the system (Default: pve1)"
	@echo "     HOST_DOMAIN            : The domain of the system (Default: cluster.daas-design.de)"
	@echo "     CEPH_DISK              : The disk to use as osd (Default: /dev/vdb)"
	@echo "     CEPH_NETWORK           : The CIDR used for ceph (Default: 192.168.100.0/24)"
	@echo "     CLUSTER_NAME           : The name used for the cluster (Default: clustertest)"
	@echo "     CLUSTER_IP             : The IP used for the cluster (Default: 192.168.200.11)"
	@echo "     LINK_IP                : The proxmox ip used to join a cluster (Default: )"
	@echo ""
	@echo "   HELP: "
	@echo "     usage             : Help message"
	@echo ""
	@echo "   EXAMPLE INSTALLATION (Standalone):"
	@echo "     export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111"
	@echo "     make proxmox-install"
	@echo "     shutdown -r now"
	@echo "     export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111"
	@echo "     make proxmox-install"
	@echo "     make daas-configure STANDALONE=yes"
	@echo "     make daas-install"
	@echo "     make daas-services"
	@echo ""
	@echo "   EXAMPLE CLUSTER: "
	@echo "     export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15"
	@echo "     HOST-1: make proxmox-cluster-create CLUSTER_NAME=daas LINK_IP=192.168.200.11"
	@echo "     HOST-2: make proxmox-cluster-join CLUSTER_IP=192.168.200.11 LINK_IP=192.168.200.12"
	@echo ""
	@echo "   EXAMPLE CEPH-INSTALL: "
	@echo "     export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15"
	@echo "     source ../web/.venv/bin/activate"
	@echo "     make proxmox-install-ceph"
	@echo "     make proxmox-install-ceph-osd CEPH_DISK=/dev/vdb"
	@echo "     make proxmox-install-ceph-cephfs"
	@echo "     make proxmox-install-ceph-pool"
	@echo ""
	@echo "     CAUTION (Ceph-All): "
	@echo "             It is recommended to create OR join a cluster before."
	@echo "             Ceph is disabled by default and must be enabled only AFTER installation!"
	@echo "             In design-config.toml enable ceph under: "
	@echo "                    - [ceph]"
	@echo "                    - [ceph.daasfs]"
	@echo ""
	@echo "     CAUTION (Ceph-Standalone): "
	@echo "             In proxmox web-ui set min-size to 1 for: "
	@echo "                    - 'daasfs_data'"
	@echo "                    - 'daasfs_metadata'"
	@echo "             In /etc/ceph/ceph.conf set: "
	@echo "                    - 'osd_pool_default_min_size = 1'"
	@echo "                    - 'osd_pool_default_size = 1'"
	@echo "             Both manual edits are only needed for ceph-standalone."
	@echo ""
	@echo "   EXAMPLE ROOT-TEMPLATES:"
	@echo "     make daas-containers"
	@echo "     make proxmox-isogen"
	@echo "     cp iso/iso/*-daas.iso /home/daas-iso/template/iso/"


# Control
start:
	systemctl $@ $(SERVICES)
stop:
	systemctl $@ $(SERVICES)

# Common
all: | proxmox-default daas-all
install: | proxmox-install daas-install
configure: | proxmox-configure daas-configure
other: | proxmox-isogen proxmox-isoupload

# Proxmox
proxmox-default: | proxmox-install proxmox-configure \
	proxmox-isogen proxmox-isoupload
proxmox-install:
	./proxmox/install.bash -i $(HOST_IP) -h $(HOST_NAME) -d $(HOST_DOMAIN)
proxmox-install-ceph: proxmox-configure
	./proxmox/ceph.bash -a ceph -n $(CEPH_NETWORK)
proxmox-install-ceph-osd:
	./proxmox/ceph.bash -a osd -n $(CEPH_NETWORK) -d $(CEPH_DISK)
proxmox-install-ceph-cephfs:
	./proxmox/ceph.bash -a cephfs -n $(CEPH_NETWORK)
proxmox-install-ceph-pool:
	./proxmox/ceph.bash -a pool -n $(CEPH_NETWORK)
proxmox-cluster-create:
	./proxmox/cluster.bash -c $(CLUSTER_NAME) -l $(LINK_IP)
proxmox-cluster-join:
	./proxmox/cluster.bash -i $(CLUSTER_IP) -l $(LINK_IP)
proxmox-configure:
	./proxmox/configure.bash -r $(DESIGN_FOLDER) -h $(HOST_NAME) -d $(HOST_DOMAIN) -i $(HOST_NUMBER)
proxmox-isogen:
	make -C iso install
	make -C iso ISOTYPE=win10 build
	make -C iso ISOTYPE=win11 build
	make -C iso ISOTYPE=debian12 build
proxmox-isoupload:
	$(PY3CMD) prox-upload-iso $(HOST_NAME) $(ISODIR)/debian12-daas.iso daas-iso
	$(PY3CMD) prox-upload-iso $(HOST_NAME) $(ISODIR)/win10-daas.iso daas-iso
	$(PY3CMD) prox-upload-iso $(HOST_NAME) $(ISODIR)/win11-daas.iso daas-iso

# Guacamole
guacamole-all: | guacamole-install guacamole-configure
guacamole/.env:
	cp ./guacamole/.env-example ./guacamole/.env
guacamole-install: guacamole/.env
	cd guacamole && ./install.bash -r $(DESIGN_FOLDER)
guacamole-configure:
	cd guacamole && ./configure.bash -r $(DESIGN_FOLDER)

# daas
daas-all: | daas-install daas-configure daas-services daas-containers
daas-install:
	cd daas && ./install.bash -r $(DESIGN_FOLDER)
daas-configure:
	cd daas && ./configure.bash -r $(DESIGN_FOLDER) -h $(HOST_NAME) \
		-d $(HOST_DOMAIN) -i $(HOST_NUMBER) -s $(STANDALONE)
daas-containers:
	make -C x11vnc commit
	make -C wine commit
daas-services:
	make -C guacd commit
	make -C rabbit commit
	make -C mariadb commit
	make -C extensions commit

# frontend
frontend-all: | frontend-configure frontend-install
frontend-install:
	cd frontend && ./install.bash -r $(DESIGN_FOLDER) -f $(FRONTEND_FOLDER)
frontend-configure:
	cd frontend && ./configure.bash -r $(DESIGN_FOLDER) \
		-f $(FRONTEND_FOLDER) -h $(HOST_NAME)

