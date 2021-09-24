PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../..))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================

config: ### Configure the contaract test environment
	make project-config

test: start run stop ### Execute the contaract test suite

start: config ### Start the contaract test project
	make docker-compose-start YML=$(DOCKER_DIR)/mockservice.docker-compose.yml

stop: ### Stop the contaract test project
	make docker-compose-stop YML=$(DOCKER_DIR)/mockservice.docker-compose.yml

run: ### Run Postman test suite against the Wiremock mappings
	make docker-run-postman \
		DIR="$(APPLICATION_TEST_DIR)/contract" \
		CMD=" \
			run Test.postman_collection.json \
			--environment=docker.postman_environment.json \
		"

reload: ### Reload the Wiremock mappings
	curl -d '' http://localhost:8080/__admin/mappings/reset
