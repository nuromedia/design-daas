.PHONY: all prepare build ensureKey start commit stop clean clean-all

TAG := daas-0-extensions
CMD := /bin/bash -i
HOSTIP := 0.0.0.0
BUILDOPT?=

all: commit

ensureKey:
	if [ ! -f ./VNCService/id_rsa.pub ] ; then \
		cp /root/.ssh/id_rsa.pub ./VNCService/id_rsa.pub ; \
	fi

build: | stop ensureKey
	cd VNCService && docker build $(BUILDOPT) -t $(TAG) .
start: build
	sudo docker run -d \
        -p "$(HOSTIP):631:631" \
        -p "$(HOSTIP):8010:8010" \
        -p "$(HOSTIP):8020:8020" \
		--name $(TAG) --rm $(TAG)
commit: start
	docker commit $(TAG)
	docker kill $(TAG)

stop:
	-docker kill $(TAG)

clean: stop
	-docker rmi $(TAG)


