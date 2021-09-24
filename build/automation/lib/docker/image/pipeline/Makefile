PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config _copy-ssl-certificate
	[ -n "$(FORCE)" ] && target=docker-build || target="docker-image-pull-or-build VERSION=$(DOCKER_LIBRARY_PIPELINE_VERSION) LATEST=true"
	make -s $$target NAME=pipeline FROM_CACHE=$(or $(FROM_CACHE), true)

test:
	make docker-test NAME=pipeline ARGS="--privileged"

push:
	make docker-push NAME=pipeline

clean:
	make docker-image-clean NAME=pipeline

# ==============================================================================

_copy-ssl-certificate:
	make ssl-copy-certificate-project DIR=$(DOCKER_LIB_IMAGE_DIR)/pipeline/assets/certificate
