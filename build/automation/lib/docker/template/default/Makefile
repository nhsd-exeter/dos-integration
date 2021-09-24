PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

dependencies:
	cd $(APPLICATION_DIR)
	tar -czf $(DOCKER_DIR)/NAME_TEMPLATE_TO_REPLACE/assets/application.tar.gz *

build: dependencies project-config _copy-ssl-certificate
	make -s docker-build NAME=NAME_TEMPLATE_TO_REPLACE

test:
	make docker-test NAME=NAME_TEMPLATE_TO_REPLACE GOSS_OPTS="GOSS_SLEEP=3"

run:
	make docker-image-start NAME=NAME_TEMPLATE_TO_REPLACE \
		DIR="$(PROJECT_DIR)/application" \
		ARGS=" \
			--publish 8443:8443 \
			--attach \
			--rm \
		"

push:
	make docker-push NAME=NAME_TEMPLATE_TO_REPLACE

clean:
	make docker-image-clean NAME=NAME_TEMPLATE_TO_REPLACE

# ==============================================================================

_copy-ssl-certificate:
	make ssl-copy-certificate-project DIR=$(DOCKER_DIR)/NAME_TEMPLATE_TO_REPLACE/assets/certificate
