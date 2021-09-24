TEST_VNC_HOST = localhost
TEST_VNC_PORT = 5900

WIREMOCK_VERSION = 2.28.0
POSTMAN_NEWMAN_VERSION = 5.2.3

# ==============================================================================

test-create-contract:
	mkdir -p $(APPLICATION_TEST_DIR_REL)/contract/mappings
	cp -fv $(LIB_DIR_REL)/test/contract/wiremock/* $(APPLICATION_TEST_DIR_REL)/contract/mappings
	cp -fv $(LIB_DIR_REL)/test/contract/postman/* $(APPLICATION_TEST_DIR_REL)/contract
	cp -fv $(LIB_DIR_REL)/test/contract/Makefile $(APPLICATION_TEST_DIR_REL)/contract
	cp -fv $(LIB_DIR_REL)/test/contract/README.md $(APPLICATION_TEST_DIR_REL)/contract
	cp -fv $(LIB_DIR_REL)/docker/compose/mockservice.docker-compose.yml $(DOCKER_DIR_REL)

# ==============================================================================

test-browser: ### Open browser VNC session
	open vnc://$(TEST_VNC_HOST):$(TEST_VNC_PORT)
	echo "The password is: 'secret'"

# ==============================================================================

.SILENT: \
	test-browser
