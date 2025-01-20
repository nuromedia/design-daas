.PHONY: all prepare build start commit stop clean clean-all

TAG := daas-0-rabbit
CMD := /bin/bash -i
HOSTIP:=172.17.0.1

all: commit

build: | stop
	docker build -t $(TAG) .
start: build
	sudo docker run -d \
		-p $(HOSTIP):4369:4369 -e RABBITMQ_HEARTBEAT=30 -p $(HOSTIP):5672:5672 \
		--name $(TAG) --rm $(TAG)
commit: start
	docker commit $(TAG)
	docker kill $(TAG)

stop:
	-docker kill $(TAG)

clean: stop
	-docker rmi $(TAG)
	rm -rf noweb


