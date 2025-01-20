.PHONY: clean

PREFIX := upstream/guacamole-common-js/src/main/webapp

guacamole.js: $(SOURCES)
	git submodule update --init
	cat $(PREFIX)/common/*.js $(PREFIX)/modules/*.js >$@

clean:
	rm guacamole.js
