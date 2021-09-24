PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config
	[ -n "$(FORCE)" ] && target=docker-build || target="docker-image-pull-or-build VERSION=$(DOCKER_LIBRARY_PYTHON_VERSION) LATEST=true"
	make -s $$target NAME=python

test:
	make docker-test NAME=python CMD="bash"

push:
	make docker-push NAME=python

clean:
	make docker-image-clean NAME=python
