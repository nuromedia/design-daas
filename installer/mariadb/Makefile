.PHONY: all prepare build ensureKey start commit stop clean clean-all

TAG := daas-0-mariadb
CMD := /bin/bash -i
HOSTIP := 127.0.0.1
BUILDOPT?=

all: commit

# ensureKey:
# 	if [ ! -f ./VNCService/id_rsa.pub ] ; then \
# 		echo foo ; \
# 		cp /root/.ssh/id_rsa.pub ./VNCService/id_rsa.pub ; \
# 	else \
# 		echo bar; \
# 	fi

build: | stop #ensureKey
	docker build $(BUILDOPT) -t $(TAG) .
start: build
	sudo docker run -d \
        -p "$(HOSTIP):3306:3306" \
	--name $(TAG) --rm $(TAG)
commit: start
	docker commit $(TAG)
	docker kill $(TAG)

stop:
	-docker kill $(TAG)

clean: stop
	-docker rmi $(TAG)


