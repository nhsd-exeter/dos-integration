PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))/../../../../../..))


# ==============================================================================

build:
	docker build --rm \
		--file Dockerfile \
		--tag kafka:2.13.0 \
		.

run-broker:
	docker run -d --name kafka-broker -p 29092:9092 kafka:2.13.0

run-create-topics:
	docker run -it --link kafka-broker \
		--name kafka kafka:2.13.0 bin/kafka-topics.sh \
		--create --bootstrap-server kafka-broker:9092 \
		--replication-factor 1 --partitions 1 --topic demoPing

test:
	make docker-test NAME=python CMD="bash"

push:
	make docker-push NAME=python

clean:
	make docker-image-clean NAME=python
