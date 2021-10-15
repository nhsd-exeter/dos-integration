PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: # Set up project
	make project-config
	make python-virtualenv
	pip install -r application/requirements.txt

build-dev:
	make docker-build NAME=serverless

build:
	make event-sender-build

stop: project-stop # Stop project

restart: stop start # Restart project

log: project-log # Show project logs

<<<<<<< d6cc7d1aa47ef32ab6f746a69a4830f6cb9a6146
=======
deploy: # Deploys whole project
	make push-images
	make serverless-deploy

undeploy: # Deploys whole project
	make serverless-remove

>>>>>>> Add aws-lambda-powertools to event sender
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
<<<<<<< d6cc7d1aa47ef32ab6f746a69a4830f6cb9a6146
=======

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

event-sender-stop:
	docker stop event-sender 2> /dev/null ||:

event-sender-trigger:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

# -----------------------------
# Serverless

push-images:
	make docker-push NAME=event-sender
# make docker-push NAME=event-receiver
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
>>>>>>> Add aws-lambda-powertools to event sender
