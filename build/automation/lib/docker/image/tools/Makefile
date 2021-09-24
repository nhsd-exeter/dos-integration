PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config
	[ -n "$(FORCE)" ] && target=docker-build || target="docker-image-pull-or-build VERSION=$(DOCKER_LIBRARY_TOOLS_VERSION) LATEST=true"
	make -s $$target NAME=tools \
		BUILD_OPTS="--build-arg PYTHON_BASE_PACKAGES='$(PYTHON_BASE_PACKAGES)'"

test:
	make docker-test NAME=tools CMD="bash"

push:
	make docker-push NAME=tools

clean:
	make docker-image-clean NAME=tools
