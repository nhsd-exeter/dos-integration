PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config
	[ -n "$(FORCE)" ] && target=docker-build || target="docker-image-pull-or-build VERSION=$(DOCKER_LIBRARY_ELASTICSEARCH_VERSION) LATEST=true"
	make -s $$target NAME=elasticsearch FROM_CACHE=$(or $(FROM_CACHE), true)

test:
	make docker-test NAME=elasticsearch \
		GOSS_OPTS="GOSS_SLEEP=$(shell [ -n "$(CIRCLE_BUILD_NUM)" ] && echo 120 || echo 30)" \
		CMD="elasticsearch"

push:
	make docker-push NAME=elasticsearch

clean:
	make docker-image-clean NAME=elasticsearch
