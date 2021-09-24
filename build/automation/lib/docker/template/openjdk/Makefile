PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config
	make -s docker-build NAME=openjdk

test:
	make docker-test NAME=openjdk CMD="bash"

push:
	make docker-push NAME=openjdk

clean:
	make docker-image-clean NAME=openjdk

# ==============================================================================

build-example:
	make docker-build NAME=openjdk EXAMPLE=true

test-example:
	make docker-test NAME=openjdk EXAMPLE=true \
		GOSS_OPTS="GOSS_SLEEP=3"

run-example:
	make docker-image-start NAME=openjdk EXAMPLE=true \
		ARGS=" \
			--workdir /application \
			--publish 8443:8443 \
			--attach \
			--rm \
		"
