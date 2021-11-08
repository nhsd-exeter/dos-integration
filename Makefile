PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: project-config # Set up project
	make docker-build NAME=serverless
	make serverless-requirements
	make python-requirements
	make mock-dos-db-setup

build: # Build lambdas
	make -s event-sender-build AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make -s event-receiver-build AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

start: # Stop project
	make project-start AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

stop: # Stop project
	make project-stop AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

restart: stop start # Restart project

log: project-log # Show project logs

deploy: # Deploys whole project - mandatory: PROFILE
	eval "$$(make populate-deployment-variables)"
	if [ "$(PROFILE)" == "task" ]; then
		make terraform-apply-auto-approve STACKS=api-key
	fi
	make terraform-apply-auto-approve STACKS=lambda-security-group
	make serverless-deploy

sls-only-deploy: # Deploys all lambdas - mandatory: PROFILE, VERSION=[commit hash-timestamp]
	eval "$$(make populate-deployment-variables)"
	make serverless-deploy

undeploy: # Undeploys whole project - mandatory: PROFILE
	make serverless-remove VERSION="any"
	make terraform-destroy-auto-approve STACKS=lambda-security-group
	if [ "$(PROFILE)" == "task" ]; then
		make terraform-destroy-auto-approve STACKS=api-key
	fi

build-and-deploy: # Builds and Deploys whole project - mandatory: PROFILE
	make build VERSION=$(BUILD_TAG)
	make push-images VERSION=$(BUILD_TAG)
	make deploy VERSION=$(BUILD_TAG)

populate-deployment-variables:
	if [ "$(PROFILE)" == "demo" ] || [ "$(PROFILE)" == "live" ] || [ "$(PROFILE)" == "dev" ]; then
		eval "$$(make aws-assume-role-export-variables)"
		echo "export DOS_API_GATEWAY_USERNAME=$$(make -s secret-get-existing-value NAME=$(DOS_DEPLOYMENT_SECRETS) KEY=$(DOS_API_GATEWAY_USERNAME_KEY))"
		echo "export DOS_API_GATEWAY_PASSWORD=$$(make -s secret-get-existing-value NAME=$(DOS_DEPLOYMENT_SECRETS) KEY=$(DOS_API_GATEWAY_PASSWORD_KEY))"
	fi

python-requirements: # Installs whole project python requirements
	make docker-run-tools \
		CMD="pip install -r requirements.txt -r requirements-dev.txt -r event_sender/requirements.txt" \
		DIR=./application

unit-test: # Runs whole project unit tests
	make -s docker-run-tools \
	CMD="python -m pytest --cov=." \
	DIR=./application \
	ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		"

coverage-report: # Runs whole project coverage unit tests
	make python-code-coverage DIR=$(APPLICATION_DIR_REL) \
	ARGS=" \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		"

component-test: # Runs whole project component tests
	make -s docker-run-tools \
	CMD="python -m behave" \
	DIR=test/component \
	ARGS=" \
		-e MOCKSERVER_URL=$(MOCKSERVER_URL) \
		-e EVENT_SENDER_FUNCTION_URL=$(EVENT_SENDER_FUNCTION_URL)\
		"

clean: # Runs whole project clean
	make \
		terraform-clean \
		python-clean \
		event-sender-clean \
		event-receiver-clean

# ==============================================================================
# Other

python-producer-run:
	make docker-run-python \
		CMD="python /project/application/producer.py"

python-consumer-run:
	make docker-run-python \
		CMD="python /project/application/consumer.py"

kafka-topic-create:
	make docker-compose-exec CMD=" \
		kafka kafka-topics --create --topic TestTopic \
			--bootstrap-server kafka:9092 \
			--replication-factor 1 \
			--partitions 1 \
	"

kafka-consumer-run:
	make docker-run \
		IMAGE=confluentinc/cp-kafka:latest \
		ARGS="--link kafka" \
		CMD=" \
			/bin/kafka-console-consumer \
				--bootstrap-server kafka:9092 \
				--topic TestTopic \
		"

kafka-producer-run:
	make docker-run \
		IMAGE=confluentinc/cp-kafka:latest \
		ARGS="--link kafka" \
		CMD=" \
			/bin/kafka-console-producer \
				--bootstrap-server kafka:9092 \
				--topic TestTopic \
		"

python-consume-message-run:
	eval "$$(make secret-fetch-and-export-variables NAME=uec-dos-int-dev/deployment)"
	python application/consume_message.py

python-peek-message-run:
	eval "$$(make secret-fetch-and-export-variables NAME=uec-dos-int-dev/deployment)"
	python application/peek_message.py

python-put-message-run:
	eval "$$(make secret-fetch-and-export-variables NAME=uec-dos-int-dev/deployment)"
	python application/put_message.py

# ==============================================================================
# Mocks Setup

mock-dos-db-setup:
	mkdir -p $(TMP_DIR)/sql 2> /dev/null ||:
	aws s3 sync s3://uec-dos-int-dos-database $(TMP_DIR)/sql

# ==============================================================================
# Common Lambda Code

common-code-copy: ### Copy common code to lambda direcory - mandatory: LAMBDA_DIR=[directory of lambda]
	cp -rf $(APPLICATION_DIR)/common $(APPLICATION_DIR)/$(LAMBDA_DIR)/

common-code-remove: ### Remove common code from lambda direcory - mandatory: LAMBDA_DIR=[directory of lambda]
	rm -rf $(APPLICATION_DIR)/$(LAMBDA_DIR)/common

# ==============================================================================
# Event Sender

event-sender-build: ### Build event sender lambda docker image
	make common-code-copy LAMBDA_DIR=event_sender
	cp -f $(APPLICATION_DIR)/event_sender/requirements.txt $(DOCKER_DIR)/event-sender/assets/requirements.txt
	cd $(APPLICATION_DIR)/event_sender
	tar -czf $(DOCKER_DIR)/event-sender/assets/event-sender-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=event-sender AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make event-sender-clean
	export VERSION=$$(make docker-image-get-version NAME=event-sender)

event-sender-clean: ### Clean event sender lambda docker image directory
	rm -fv $(DOCKER_DIR)/event-sender/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/event-sender/assets/*.txt
	make common-code-remove LAMBDA_DIR=event_sender

event-sender-run: ### A rebuild and restart of the event sender lambda.
	make stop
	make event-sender-build
	make start

# ==============================================================================
# Event receiver

event-receiver-build:
	make common-code-copy LAMBDA_DIR=event_receiver
	cp -f $(APPLICATION_DIR)/event_receiver/requirements.txt $(DOCKER_DIR)/event-receiver/assets/requirements.txt
	cd $(APPLICATION_DIR)/event_receiver
	tar -czf $(DOCKER_DIR)/event-receiver/assets/event-receiver-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=event-receiver AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make event-receiver-clean
	export VERSION=$$(make docker-image-get-version NAME=event-receiver)

event-receiver-clean: ### Clean event receiver lambda docker image directory
	rm -fv $(DOCKER_DIR)/event-receiver/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/event-receiver/assets/*.txt
	make common-code-remove LAMBDA_DIR=event_receiver

event-receiver-run: ### A rebuild and restart of the event receiver lambda.
	make stop
	make event-receiver-build
	make start

# -----------------------------
# Serverless

push-images: # Use VERSION=[] to push a perticular version otherwise with default to latest
	make docker-push NAME=event-receiver AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make docker-push NAME=event-sender AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
# make docker-push NAME=event-processor

serverless-requirements: # Install serverless plugins
	make serverless-install-plugin NAME="serverless-vpc-discovery"
	make serverless-install-plugin NAME="serverless-localstack"

# -----------------------------
# Other

create-ecr-repositories:
	make docker-create-repository NAME=event-processor
	make docker-create-repository NAME=event-receiver
	make docker-create-repository NAME=event-sender
