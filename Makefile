PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: # Set up project
	make project-config
	make python-virtualenv
	pip install -r application/requirements.txt

build-dev: #Build dev requirements
	make docker-build NAME=serverless
	make serverless-requirements
	make python-requirements

build:
	make event-sender-build

stop: project-stop # Stop project

restart: stop start # Restart project

log: project-log # Show project logs

deploy: # Deploys whole project - mandatory: PROFILE
	make serverless-deploy

undeploy: # Undeploys whole project - mandatory: PROFILE
	make serverless-remove VERSION="any"

build-and-deploy: # - mandatory: PROFILE
	make build VERSION=$(BUILD_TAG)
	make push-images VERSION=$(BUILD_TAG)
	make deploy VERSION=$(BUILD_TAG)

python-requirements: # Installs whole project python requirements
	make docker-run-tools \
		CMD="pip install -r requirements.txt -r requirements-dev.txt -r event_sender/requirements.txt" \
		DIR=./application

unit-test: # Runs whole project unit tests
	make -s docker-run-tools \
	CMD="python -m pytest --cov=. " \
	DIR=application \
	ARGS="-e POWERTOOLS_TRACE_DISABLED=1"

coverage-report: # Runs whole project coverage unit tests
	make python-code-coverage DIR=./application \
	ARGS="-e POWERTOOLS_TRACE_DISABLED=1"

clean: # Runs whole project clean
	make python-clean

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
# Common Lambda Code

common-code-copy: ### Copy common code to lambda direcory - mandatory: LAMBDA_DIR=[directory of lambda]
	cp -rf $(APPLICATION_DIR)/common $(APPLICATION_DIR)/$(LAMBDA_DIR)/

common-code-remove: ### Remove common code from lambda direcory - mandatory: LAMBDA_DIR=[directory of lambda]
	rm -rf $(APPLICATION_DIR)/$(LAMBDA_DIR)/common

# ==============================================================================
# Event Sender

event-sender-build: ### Build event sender lambda docker image
	make common-code-copy LAMBDA_DIR=event_sender
	cd $(APPLICATION_DIR)/event_sender
	tar -czf $(DOCKER_DIR)/event-sender/assets/event-sender-app.tar.gz \
		--exclude=tests \
		*.py \
		common \
		requirements.txt
	cd $(PROJECT_DIR)
	make docker-image NAME=event-sender AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make event-sender-clean
	export VERSION=$$(make docker-image-get-version NAME=event-sender)

event-sender-clean: ### Clean event sender lambda docker image directory
	rm -fv $(DOCKER_DIR)/event-sender/assets/event-sender-app.tar.gz
	make common-code-remove LAMBDA_DIR=event_sender

event-sender-stop: ### Stop running event sender lambda
	docker stop event-sender 2> /dev/null ||:

event-sender-start: ### Start event sender lambda
	make docker-run IMAGE=$(DOCKER_REGISTRY)/event-sender:latest ARGS=" \
	-d \
	-p 9000:8080 \
	-e FUNCTION_NAME=event-sender \
	-e LOG_LEVEL=INFO \
	-e POWERTOOLS_METRICS_NAMESPACE="dos-integration" \
	-e POWERTOOLS_SERVICE_NAME="event-sender" \
	" \
	CONTAINER="event-sender"

event-sender-trigger: ### Trigger event sender lambda
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"message": "hello world", "username": "lessa"}'

event-sender-run: ### A rebuild and restart of the event sender lambda.
	make event-sender-stop
	make event-sender-build
	make event-sender-start
	make event-sender-trigger

# -----------------------------
# Serverless

push-images: # Use VERSION=[] to push a perticular version otherwise with default to latest
	make docker-push NAME=event-sender AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
# make docker-push NAME=event-processor
# make docker-push NAME=event-receiver

serverless-requirements: # Install serverless plugins
	make serverless-install-plugin NAME="serverless-vpc-discovery"
	make serverless-install-plugin NAME="serverless-localstack"

# -----------------------------
# CI/CD

parse-profile-from-tag: # Return profile based off of git tag - Mandatory GIT_TAG=[git tag]
	echo $(GIT_TAG) | cut -d "-" -f2

parse-profile-from-branch: # Return profile based off of git branch - Mandatory BRANCH_NAME=[git branch name]
	if [ $(BRANCH_NAME) == "master" ]; then
		echo "dev"
	else
		echo "task"
	fi


# -----------------------------
# Other

create-ecr-repositories:
	make docker-create-repository NAME=event-processor
	make docker-create-repository NAME=event-receiver
	make docker-create-repository NAME=event-sender
