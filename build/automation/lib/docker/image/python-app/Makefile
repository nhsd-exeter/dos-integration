PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config _copy-ssl-certificate
	[ -n "$(FORCE)" ] && target=docker-build || target="docker-image-pull-or-build VERSION=$(DOCKER_LIBRARY_PYTHON_APP_VERSION) LATEST=true"
	make -s $$target NAME=python-app

test:
	make docker-test NAME=python-app CMD="bash"

push:
	make docker-push NAME=python-app

clean:
	make docker-image-clean NAME=python-app

# ==============================================================================

build-example:
	make docker-build NAME=python-app EXAMPLE=true FORCE=true

test-example:
	make docker-test NAME=python-app EXAMPLE=true \
		GOSS_OPTS="GOSS_SLEEP=3"

run-example:
	make docker-image-start NAME=python-app EXAMPLE=true \
		ARGS=" \
			--workdir /application \
			--publish 8443:8443 \
			--attach \
			--rm \
		"

# ==============================================================================

_copy-ssl-certificate:
	make ssl-copy-certificate-project DIR=$(DOCKER_LIB_IMAGE_DIR)/python-app/assets/certificate
