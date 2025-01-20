.PHONY: all build prepare start commit stop clean

TAG := x11vnc
PORT ?= 5901
CMD := /bin/bash -i
QMSGDIR := ../../src/app/daas/messaging
PASSWORD := user1234
BUILDOPT ?= 
all: commit

prepare:
	rm -rf qmsg
	cp -r $(QMSGDIR) qmsg
	#sudo chmod -R a+rwx noweb

build: | stop prepare
	docker build $(BUILDOPT) -t $(TAG) .

start: build
	docker run -d -p 127.0.0.1:$(PORT):5900 -p 127.0.0.1:2221:22 \
		--name $(TAG) --rm  $(TAG) $(CMD)

commit: start
	#docker commit $(TAG)
	docker kill $(TAG)

stop:
	-docker kill $(TAG)

clean: stop
	-docker rmi $(TAG)
