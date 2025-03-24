# ------------------------------------------------------------------------------
# --- Defaults
# ------------------------------------------------------------------------------
# Makefiel setup
.PHONY: default usage install \
	start stop clean \
	plots  plots-clean \
	tests-all tests-curl tests-curl-clean \
	tests-firefox tests-firefox-clean \
	tests-all-clean\
	local-start local-stop \
	docker-build docker-rebuild \
	docker-start docker-stop \
	docker-connect docker-clean
default: local-start
# Shell setup
SHELL:=/bin/bash
# Vars
IMGNAME?=skeleton
CONTNAME?=$(IMGNAME)
VENV_INST="quart quart-cors requests aiohttp websockets flake8 pylint pika netifaces psutil sqlalchemy pymysql pylint-per-file-ignores black types-requests types-click types-aiofiles pandas matplotlib nest_asyncio aiosqlite docker"
LPORT?=4444
RPORT?=4444
DIR_RESULTS="data/results"
TEST_NAME?="out"
TEST_ITER?=10
TEST_SLEEP?=1
# TEST_DOMAIN?="http://localhost:4444"
# TEST_DOMAIN?="https://cluster.daas-design.de:5000"
TEST_DOMAIN?="https://pve.cluster.local"
# ------------------------------------------------------------------------------
# --- Help
# ------------------------------------------------------------------------------
usage:
	@echo "make TARGET"
	@echo "   TARGETS: "
	@echo "     usage: Help message"
	@echo ""
	@echo "     build: Build container"
	@echo "     start: Start container"
	@echo "     stop : Stop container"
	@echo "     clean: Clean conatiner and images"
	@echo ""
# ------------------------------------------------------------------------------
# --- Host targets
# ------------------------------------------------------------------------------
install:
	@echo "--- LOCAL INSTALL ----------------"
	rm -rf .venv
	apt -y install parallel
	mkdir -p data/keys
	./scripts/ensure_venv.bash -p $(VENV_INST)
	./scripts/genkey.bash -f -n $(IMGNAME)
local-start:stop
	@echo "--- LOCAL START ------------------"
	@source ./.venv/bin/activate && python3 main.py 
local-stop:
	@echo "--- LOCAL STOP -------------------"
	-pkill -f "python3 main.py"
# ------------------------------------------------------------------------------
# --- Test targets
# ------------------------------------------------------------------------------
tests-all: | tests-curl tests-firefox
tests-firefox: tests-firefox-clean
	@echo "Generate CSV via Browser: $(TEST_DOMAIN)"
	@./scripts/tests_browser.bash \
		-i $(TEST_ITER) \
		-d $(TEST_DOMAIN) \
		-o $(DIR_RESULTS)/csv \
		-s $(TEST_SLEEP) \
		-u baseline0 \
		-u baseline1 \
		-u baseline2 \
		-u baseline3 \
		-u baseline4 \
		-u baseline5 \
		-u baseline6

tests-curl: tests-curl-clean
	@echo "Generate CSV via Curl:"
	@./scripts/tests_curl.bash \
		-i $(TEST_ITER) \
		-d $(TEST_DOMAIN) \
		-o $(DIR_RESULTS)/csv \
		-s $(TEST_SLEEP) \
		-u baseline0 \
		-u baseline1 \
		-u baseline2 \
		-u baseline3 \
		-u baseline4 \
		-u baseline5 \
		-u baseline6

tests-firefox-clean:
	@-rm -rf ~/Downloads/firefox-*.csv
	@-rm -rf $(DIR_RESULTS)/csv/firefox-*
tests-curl-clean:
	@-rm -rf $(DIR_RESULTS)/csv/curl-*
tests-all-clean: tests-curl-clean tests-firefox-clean
	@-rm -rf $(DIR_RESULTS)/csv
# ------------------------------------------------------------------------------
# --- Plot targets
# ------------------------------------------------------------------------------
plots: plots-clean
	@echo "Creating plots:"
	@source .venv/bin/activate \
		&& python3 ./scripts/plot_columns.py \
		&& python3 ./scripts/plot_origins.py \
		&& python3 ./scripts/plot_domains.py \
		&& python3 ./scripts/plot_methods.py\
		&& python3 ./scripts/plot_combined.py
	@mkdir -p $(DIR_RESULTS)/plots/$(TEST_NAME)
	@cp -r $(DIR_RESULTS)/csv $(DIR_RESULTS)/plots/$(TEST_NAME)
	@mv $(DIR_RESULTS)/columns \
		$(DIR_RESULTS)/origins \
		$(DIR_RESULTS)/domains \
		$(DIR_RESULTS)/methods \
		$(DIR_RESULTS)/combined \
		$(DIR_RESULTS)/plots/$(TEST_NAME)

plots-clean:
	@-rm -rf $(DIR_RESULTS)/plots/$(TEST_NAME)
	@-rm -rf $(DIR_RESULTS)/columns \
		$(DIR_RESULTS)/origins \
		$(DIR_RESULTS)/domains \
		$(DIR_RESULTS)/methods \
		$(DIR_RESULTS)/combined
# ------------------------------------------------------------------------------
# --- Docker targets
# ------------------------------------------------------------------------------
docker-rebuild: docker-stop
	@echo "--- DOCKER REBUILD ---------------"
	@docker build -t $(IMGNAME) --no-cache .
docker-build: docker-stop
	@echo "--- DOCKER BUILD -----------------"
	@docker build -t $(IMGNAME) .
docker-start: docker-build
	@echo "--- DOCKER START -----------------"
	@docker run \
		-p $(LPORT):$(RPORT) \
		-v `pwd`/app:/opt/qweb/app \
		-v `pwd`/data/webroot:/opt/qweb/data/webroot \
		-v `pwd`/data/keys:/opt/qweb/data/keys \
		-d --rm --name $(CONTNAME) $(IMGNAME)
	@docker logs -f $(CONTNAME) &
docker-stop:
	@echo "--- DOCKER STOP ------------------"
	@-docker kill $(CONTNAME)
docker-connect:
	@docker exec -it $(CONTNAME) bash
docker-clean: docker-stop
	@-docker rm $(CONTNAME)
	@-docker image rm $(IMGNAME)
# ------------------------------------------------------------------------------
# --- Common targets
# ------------------------------------------------------------------------------
start: | stop default
	
stop: docker-stop local-stop

clean: docker-clean tests-all-clean plots-clean
