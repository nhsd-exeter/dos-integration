PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

build: project-config _copy-ssl-certificate
	[ -n "$(FORCE)" ] && target=docker-build || target="docker-image-pull-or-build VERSION=$(DOCKER_LIBRARY_POSTGRES_VERSION) LATEST=true"
	make -s $$target NAME=postgres FROM_CACHE=$(or $(FROM_CACHE), true)

test:
	make \
		_test-sql \
		_test-scripts \
		_test-postgres

_test-sql:
	make _test-prerequisites-setup
	make docker-run-postgres \
		ARGS=" \
			--env DB_HOST=postgres.$(PROJECT_NAME_SHORT).local \
			--env WAIT_FOR=postgres.$(PROJECT_NAME_SHORT).local:5432 \
		" \
		CMD='sql "select version();"'
	make _test-prerequisites-teardown

_test-scripts:
	make _test-prerequisites-setup
	make docker-run-postgres \
		ARGS=" \
			--env DB_HOST=postgres.$(PROJECT_NAME_SHORT).local \
			--env WAIT_FOR=postgres.$(PROJECT_NAME_SHORT).local:5432 \
			--volume $(DOCKER_LIB_IMAGE_DIR)/postgres/assets/data:/data \
		" \
		CMD="scripts"
	make _test-prerequisites-teardown

_test-postgres:
	make docker-test NAME=postgres \
		GOSS_OPTS="GOSS_SLEEP=3" \
		ARGS=" \
			--env DB_NAME=test \
			--env DB_USERNAME=test \
			--env DB_PASSWORD=test \
		" \
		CMD="postgres"

push:
	make docker-push NAME=postgres

clean:
	make docker-image-clean NAME=postgres

# ==============================================================================

_copy-ssl-certificate:
	make ssl-copy-certificate-project DIR=$(DOCKER_LIB_IMAGE_DIR)/postgres/assets/etc/postgresql

_test-prerequisites-setup:
	make _TEST_POSTGRES_SQL_FILE
	make \
		docker-compose-stop ALL=true \
		docker-compose-start \
		YML=$(DOCKER_LIB_IMAGE_DIR)/postgres/test/docker-compose.postgres.yml

_test-prerequisites-teardown:
	make \
		docker-compose-stop ALL=true \
		YML=$(DOCKER_LIB_IMAGE_DIR)/postgres/test/docker-compose.postgres.yml
	rm -rf $(_TEST_POSTGRES_SQL_FILE)*

_TEST_POSTGRES_SQL_FILE := $(DOCKER_LIB_IMAGE_DIR)/postgres/assets/data/00-version.sql
_TEST_POSTGRES_SQL_FILE:
	echo "select version();" > $(_TEST_POSTGRES_SQL_FILE)
	gzip -c $(_TEST_POSTGRES_SQL_FILE) > $(_TEST_POSTGRES_SQL_FILE).gz
