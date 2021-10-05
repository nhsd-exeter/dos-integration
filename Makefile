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
