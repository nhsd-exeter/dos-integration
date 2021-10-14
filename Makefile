PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: # Set up project
	make project-config
	make python-virtualenv
	pip install -r application/requirements.txt

start: project-start # Start project

stop: project-stop # Stop project

restart: stop start # Restart project

log: project-log # Show project logs

deploy: # Deploys whole project
	make serverless-run

python-requirements:
	make docker-run-tools \
		CMD="pip install -r requirements.txt" \
		DIR=./application

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

python-pytest:
	make docker-run-tools CMD=" \
		pip install -r requirements.txt && \
		python -m pytest application/tests -s -x -v \
	" \
	DIR=./application

coverage-report:
	make python-code-coverage DIR=./application

clean:
	make python-clean

# ==============================================================================
# Event Sender

event-sender-build:
	cd $(APPLICATION_DIR)/event_sender
	tar -czf $(DOCKER_DIR)/event-sender/assets/event-sender-app.tar.gz \
		*.py \
		requirements.txt
	cd $(PROJECT_DIR)
	make docker-image NAME=event-sender
	make event-sender-clean

event-sender-clean: ## Clean up
	rm -fv $(DOCKER_DIR)/event-sender/assets/event-sender-app.tar.gz

event-sender-run:
	echo hi

event-sender-start:
	make docker-run IMAGE=$(DOCKER_REGISTRY)/event-sender:latest ARGS=" \
	-d \
	-p 9000:8080 \
	" \
	CONTAINER="event-sender"

event-sender-trigger:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

# -----------------------------
# Serverless

serverless-deploy: # Deploy AWS resources
	make serverless-run CMD=deploy

serverless-remove: # Delete existing AWS resources
	make serverless-run CMD=remove

serverless-info: # See info on deployed environment
	make serverless-run CMD=info

serverless-run: # Runs serverless commands
	if [ "$(PROFILE)" == "local" ]; then
		make -s localstack-start
		export SLS_DEBUG=true
		serverless $(CMD) --config $(or $(CONFIG_FILE), serverless.yml) --stage $(PROFILE)
	elif [ "$(PROFILE)" == "task" ]; then
		make docker-run-serverless IMAGE=$(DOCKER_REGISTRY)/serverless CMD="serverless $(CMD) --config $(or $(CONFIG_FILE), serverless.yml) --stage $(ENVIRONMENT)"
	else
		make docker-run-serverless IMAGE=$(DOCKER_REGISTRY)/serverless CMD="serverless $(CMD) --config $(or $(CONFIG_FILE), serverless.yml) --stage $(PROFILE)"
	fi

serverless-clean:
	rm -rf .serverless

serverless-plugin-install: # Install serverless plugins
	make docker-run-serverless IMAGE=$(DOCKER_REGISTRY)/serverless CMD="serverless plugin install -n serverless-localstack"
	make docker-run-serverless IMAGE=$(DOCKER_REGISTRY)/serverless CMD="serverless plugin install -n serverless-vpc-discovery"

docker-run-serverless:
	make docker-config > /dev/null 2>&1
		container=$$([ -n "$(CONTAINER)" ] && echo $(CONTAINER) || echo $$(echo '$(IMAGE)' | md5sum | cut -c1-7)-$(BUILD_COMMIT_HASH)-$(BUILD_ID)-$$(date --date=$$(date -u +"%Y-%m-%dT%H:%M:%S%z") -u +"%Y%m%d%H%M%S" 2> /dev/null)-$$(make secret-random LENGTH=8))
		docker run --interactive $(_TTY) --rm \
			--name $$container \
			--env-file <(make _list-variables PATTERN="^(AWS|TX|TEXAS|NHSD|TERRAFORM)") \
			--env-file <(make _list-variables PATTERN="^(DB|DATABASE|SMTP|APP|APPLICATION|UI|API|SERVER|HOST|URL)") \
			--env-file <(make _list-variables PATTERN="^(PROFILE|ENVIRONMENT|BUILD|PROGRAMME|ORG|SERVICE|PROJECT)") \
			--env-file <(make _docker-get-variables-from-file VARS_FILE=$(VARS_FILE)) \
			--volume $(PROJECT_DIR):/project \
			--network $(DOCKER_NETWORK) \
			--workdir /project/$(shell echo $(abspath $(DIR)) | sed "s;$(PROJECT_DIR);;g") \
			$(ARGS) \
			$(IMAGE) \
				$(CMD)

# -----------------------------
# Other

create-ecr-repositories:
	make docker-create-repository NAME=event-processor
	make docker-create-repository NAME=event-receiver
	make docker-create-repository NAME=event-sender
