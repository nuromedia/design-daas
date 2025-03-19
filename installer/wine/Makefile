.PHONY: all prepare build start commit stop clean clean-all

TAG := wine
PORT := 5900
CMD := /bin/bash -i
PASSWORD := user1234
QMSGDIR := ../../src/app/daas/messaging
QINSTDIR := ../../src/app/inst
APP_URL := https://download-installer.cdn.mozilla.net/pub/thunderbird/releases/115.6.1/win64/de/Thunderbird%20Setup%20115.6.1.exe
BUILDOPT ?=
all: commit

prepare:
	rm -rf qmsg
	mkdir -p qmsg/env
	cp -r $(QMSGDIR)/* qmsg
	cp -r $(QINSTDIR)/* qmsg/env
	cp /root/.ssh/id_rsa.pub authorized_keys
	sudo chmod -R a+rwx qmsg
	if [ ! -f ./app.exe ]; then \
		curl -o app.exe $(APP_URL) ; \
	fi

build: | stop prepare
	docker build $(BUILDOPT) -t $(TAG) .

start: build
	sudo docker run -d \
		-p 0.0.0.0:$(PORT):$(PORT) -p 127.0.0.1:2222:22 \
		--name $(TAG) --rm  $(TAG) $(CMD)

commit: start
	docker commit $(TAG)
	docker kill $(TAG)

stop:
	-docker kill $(TAG)

clean: stop
	-docker rmi $(TAG)
	rm -rf noweb

