
.PHONY: all

SHELL := /bin/bash
USERNAME?=root
USERPASS?=root
QCOWSIZE?=256
VMSSHPORT?=5555
EXTRAPORTS?=0
TIMEOUTS?=10000
ISOFOLDER:=iso
OUTFOLDER:=out
ISOTYPE?=win10
INCFOLDER?=cfg/$(ISOTYPE)
ISONAME:=$(ISOTYPE)-daas

all: help
full: | install rebuild startnew ssh
startnew: | disk start
rebuild: | clean build

help:
	@echo "make [OPTION=OPTION_VALUE] [TARGET]"
	@echo ""
	@echo "   TARGETS "
	@echo "      clean     : Invokes clean on all generate scripts"
	@echo "      clean-all : Removes all generated (iso, images, tmp-files)"
	@echo "      install   : Install prerequisites (qemu-kvm,isolinux,etc.)"
	@echo "      build     : Builds a specified iso"
	@echo "      disk      : Creates qcow-disk for test vm"
	@echo "      start     : Runs the generated iso in a test vm"
	@echo "      stop      : Stops a running test vm"
	@echo "      ssh       : Connects via ssh to the test vm"
	@echo "   OPTIONS "
	@echo "      USERNAME  : Username for installation and ssh connect"
	@echo "      USERPASS  : Initial password set during installation"
	@echo "      QCOWSIZE  : Maximum disk size for test vm"
	@echo "      VMSSHPORT : Local port mapped to test vm (Default: 5555)"
	@echo "      EXTRAPORTS: Also map daas-design ports (8006,8080,5000,3000)"
	@echo "      TIMEOUTS  : ssh connects until waitphase fails"
	@echo "      ISO_TYPE  : The generated iso type (debian12,win10,devenv)"
	@echo "      INCFOLDER : The config folder being used"
	@echo ""
	@echo "Remarks:"
	@echo "The Makefile awaits an iso type, a corresponding generate-script"
	@echo " and a config folder containing required scripts and config files."
	@echo "These depend on the architecture being generated as well as the "
	@echo "related generate-script which copies specific data into the iso."
	@echo "A also provided postinstall-script utilizes then this copied data"
	@echo "during automated installation and upon the first system reboot."
	@echo "This might be in the simplest case just a public/private keypair"
	@echo "for automated ssh-connections but can be any other data as well."
	@echo "Only RSA is supported for now. Hence, a keypair must have the name"
	@echo "'id_rsa'/'id_rsa.pub' and has to be placed in 'cfg/ISOTYPE/ssh/'."
	@echo "If no keypair is provided a new one will be generated on the fly."
	@echo ""
	@echo "Examples: "
	@echo "make ISOTYPE=debian12 build"
	@echo "make ISOTYPE=debian12 QCOWSIZE=128 disk"
	@echo "make ISOTYPE=debian12 VMSSHPORT=12345 start"
	@echo "make ISOTYPE=debian12 VMSSHPORT=12345 TIMEOUTS=500 ssh"
	@echo ""

clean: stop
	@./scripts/generate-win10-iso.bash -a clean
	@./scripts/generate-debian12-iso.bash -a clean

clean-all: clean
	@-rm -rf $(QCOWIMAGE) $(ISOFOLDER)
	@-sudo rm -rf $(OUTFOLDER)

install:
	@echo "Install essentials..."
	@./scripts/vm-run.bash -a install
	@./scripts/generate-win10-iso.bash -a install
	@./scripts/generate-debian12-iso.bash -a install

build:
	@echo "Create Iso..."
	@./scripts/generate-$(ISOTYPE)-iso.bash -a generate -i $(INCFOLDER) \
		-p $(USERPASS) -n $(ISONAME) -u $(USERNAME)

build-cluster:
	@echo "Create Cluster-Iso..."
	@./scripts/generate-devenv-iso.bash -a generate -i $(INCFOLDER) \
		-p $(USERPASS) -n devenv -u $(USERNAME)

disk:
	@echo "Create disk..."
	@./scripts/vm-run.bash -a disk -n $(ISONAME) -s $(QCOWSIZE)

disk-cluster:
	@echo "Create disks..."
	@./scripts/cluster-run.bash -a disk -n pve1 -s $(QCOWSIZE)
	@./scripts/cluster-run.bash -a disk -n pve2 -s $(QCOWSIZE)
	@./scripts/cluster-run.bash -a disk -n pve3 -s $(QCOWSIZE)

start:
	@echo "Run VM..."
	@./scripts/vm-run.bash -a start \
		-n $(ISONAME) -p $(VMSSHPORT) -e $(EXTRAPORTS)

start-cluster:
	@echo "Run Cluster..."
	@./scripts/cluster-run.bash -a netstart
	@./scripts/cluster-run.bash -a start -n pve1
	@./scripts/cluster-run.bash -a start -n pve2
	@./scripts/cluster-run.bash -a start -n pve3

stop:
	@echo "Stop VM..."
	@./scripts/vm-run.bash -a stop -n $(ISONAME)

stop-cluster:
	@echo "Stop Cluster..."
	@./scripts/cluster-run.bash -a stop -n pve1
	@./scripts/cluster-run.bash -a stop -n pve2
	@./scripts/cluster-run.bash -a stop -n pve3
	@./scripts/cluster-run.bash -a netstop

ssh:
	@echo "Connect VM..."
	@./scripts/vm-connect.bash -a connect -n $(ISONAME) \
		-p $(VMSSHPORT) -u $(USERNAME) -i $(INCFOLDER) \
		-f pve -t $(TIMEOUTS)

