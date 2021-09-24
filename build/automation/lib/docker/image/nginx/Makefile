PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config _copy-ssl-certificate
	[ -n "$(FORCE)" ] && target=docker-build || target="docker-image-pull-or-build VERSION=$(DOCKER_LIBRARY_NGINX_VERSION) LATEST=true"
	make -s $$target NAME=nginx

test:
	make docker-test NAME=nginx

push:
	make docker-push NAME=nginx

clean:
	make docker-image-clean NAME=nginx

# ==============================================================================

build-example:
	make docker-build NAME=nginx EXAMPLE=true FORCE=true

test-example:
	make docker-test NAME=nginx EXAMPLE=true

run-example:
	make docker-image-start NAME=nginx EXAMPLE=true \
		ARGS=" \
			--workdir /application \
			--publish 8080:8080 \
			--publish 8443:8443 \
			--attach \
			--rm \
		"

# ==============================================================================

_copy-ssl-certificate:
	make ssl-copy-certificate-project DIR=$(DOCKER_LIB_IMAGE_DIR)/nginx/assets/certificate
