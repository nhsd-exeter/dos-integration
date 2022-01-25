PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: project-config # Set up project
	make docker-build NAME=serverless
	make serverless-requirements
	make tester-build
	make mock-dos-db-setup

build: # Build lambdas
	make -s event-sender-build AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make -s event-processor-build AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make -s fifo-dlq-handler-build AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

start: # Stop project
	make project-start AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

stop: # Stop project
	make project-stop AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

restart: stop start # Restart project

log: project-log # Show project logs

deploy: # Deploys whole project - mandatory: PROFILE
	if [ "$(PROFILE)" == "task" ]; then
		make terraform-apply-auto-approve STACKS=api-key,change-request-receiver-api-key
	fi
	if [ "$(PROFILE)" == "task" ] || [ "$(PROFILE)" == "dev" ] || [ "$(PROFILE)" == "perf" ]; then
		make authoriser-build-and-push dos-api-gateway-build-and-push
		make terraform-apply-auto-approve STACKS=dos-api-gateway-mock
	fi
	eval "$$(make -s populate-deployment-variables)"
	make terraform-apply-auto-approve STACKS=lambda-security-group,lambda-iam-roles,dynamo-db
	make serverless-deploy
	make terraform-apply-auto-approve STACKS=change-request-receiver-route53,eventbridge,api-gateway-sqs,splunk-logs

undeploy: # Undeploys whole project - mandatory: PROFILE
	eval "$$(make -s populate-deployment-variables)"
	make terraform-destroy-auto-approve STACKS=evenbridge,change-request-receiver-route53,splunk-logs,api-gateway-sqs
	make serverless-remove VERSION="any" DB_PASSWORD="any"
	make terraform-destroy-auto-approve STACKS=lambda-security-group,lambda-iam-roles
	if [ "$(PROFILE)" == "task" ]; then
		make terraform-destroy-auto-approve STACKS=api-key,change-request-receiver-api-key
	fi
	if [ "$(PROFILE)" == "task" ] || [ "$(PROFILE)" == "dev" ]; then
		make terraform-destroy-auto-approve STACKS=dos-api-gateway-mock,dynamo-db
	fi

build-and-deploy: # Builds and Deploys whole project - mandatory: PROFILE
	make build VERSION=$(BUILD_TAG)
	make push-images VERSION=$(BUILD_TAG)
	make deploy VERSION=$(BUILD_TAG)

populate-deployment-variables:
	eval "$$(make aws-assume-role-export-variables)"
	echo "export DB_SERVER=$$(make -s aws-rds-describe-instance-value DB_INSTANCE=$(DB_SERVER_NAME) KEY_DOT_PATH=Endpoint.Address)"
	echo "export DB_USER_NAME=$$(make -s secret-get-existing-value NAME=$(DB_USER_NAME_SECRET_NAME) KEY=$(DB_USER_NAME_SECRET_KEY))"

unit-test:
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester \
	CMD="python -m pytest --junitxml=./testresults.xml --cov=. -vv" \
	DIR=./application \
	ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/authoriser:/tmp/.packages/authoriser \
		--volume $(APPLICATION_DIR)/dos_api_gateway:/tmp/.packages/dos_api_gateway \
		--volume $(APPLICATION_DIR)/event_processor:/tmp/.packages/event_processor \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/fifo_dlq_handler \
		"

coverage-report: # Runs whole project coverage unit tests
	make -s python-code-coverage DIR=$(APPLICATION_DIR_REL) \
	IMAGE=$$(make _docker-get-reg)/tester \
	ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/authoriser:/tmp/.packages/authoriser \
		--volume $(APPLICATION_DIR)/dos_api_gateway:/tmp/.packages/dos_api_gateway \
		--volume $(APPLICATION_DIR)/event_processor:/tmp/.packages/event_processor \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/fifo_dlq_handler \
		"

e2e-test-smoke: #End to end test DI project - mandatory: PROFILE, ENVIRONMENT=test
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester \
	CMD="python -m behave features/e2e_di_test.feature --no-capture" \
	DIR=./test/integration \
	ARGS=" \
		-e API_KEY_SECRET=$(TF_VAR_api_gateway_api_key_name) \
		-e NHS_UK_API_KEY=$(TF_VAR_nhs_uk_api_key_key) \
		-e DOS_DB_PASSWORD_SECRET_NAME=$(DB_SECRET_NAME) \
		-e DOS_DB_PASSWORD_KEY=$(DB_SECRET_KEY) \
		-e DOS_DB_USERNAME_SECRET_NAME=$(DB_USER_NAME_SECRET_NAME) \
		-e DOS_DB_USERNAME_KEY=$(DB_USER_NAME_SECRET_KEY) \
		-e URL=https://$(DOS_INTEGRATION_URL) \
		-e EVENT_PROCESSOR=$(TF_VAR_event_processor_lambda_name) \
		-e EVENT_SENDER=$(TF_VAR_event_sender_lambda_name) \
		-e SQS_URL=$(SQS_QUEUE_URL) \
		-e DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
		-e DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
		"

e2e-test: #End to end test DI project - mandatory: PROFILE, TAGS=[complete|dev]; optional: ENVIRONMENT
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester \
	CMD="python -m behave --no-capture --tags=$(TAGS)" \
	DIR=./test/integration \
	ARGS=" \
		-e API_KEY_SECRET=$(TF_VAR_api_gateway_api_key_name) \
		-e NHS_UK_API_KEY=$(TF_VAR_nhs_uk_api_key_key) \
		-e DOS_DB_PASSWORD_SECRET_NAME=$(DB_SECRET_NAME) \
		-e DOS_DB_PASSWORD_KEY=$(DB_SECRET_KEY) \
		-e DOS_DB_USERNAME_SECRET_NAME=$(DB_USER_NAME_SECRET_NAME) \
		-e DOS_DB_USERNAME_KEY=$(DB_USER_NAME_SECRET_KEY) \
		-e URL=https://$(DOS_INTEGRATION_URL) \
		-e EVENT_PROCESSOR=$(TF_VAR_event_processor_lambda_name) \
		-e EVENT_SENDER=$(TF_VAR_event_sender_lambda_name) \
		-e SQS_URL=$(SQS_QUEUE_URL) \
		-e DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
		-e DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
		"

clean: # Runs whole project clean
	make \
		docker-clean \
		terraform-clean \
		serverless-clean \
		python-clean \
		event-sender-clean \
		event-processor-clean \
		tester-clean \
		authoriser-clean \
		dos-api-gateway-clean

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
# Event Processor

event-processor-build: ### Build event processor lambda docker image
	make common-code-copy LAMBDA_DIR=event_processor
	cp -f $(APPLICATION_DIR)/event_processor/requirements.txt $(DOCKER_DIR)/event-processor/assets/requirements.txt
	cd $(APPLICATION_DIR)/event_processor
	tar -czf $(DOCKER_DIR)/event-processor/assets/event-processor-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=event-processor AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make event-processor-clean
	export VERSION=$$(make docker-image-get-version NAME=event-processor)

event-processor-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/event-processor/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/event-processor/assets/*.txt
	make common-code-remove LAMBDA_DIR=event_processor

event-processor-run: ### A rebuild and restart of the event processor lambda.
	make stop
	make event-processor-build
	make start

# ==============================================================================
# First In First Out Dead Letter Queue Handler (fifo-dlq-handler)

fifo-dlq-handler-build: ### Build event processor lambda docker image
	make common-code-copy LAMBDA_DIR=fifo_dlq_handler
	cp -f $(APPLICATION_DIR)/fifo_dlq_handler/requirements.txt $(DOCKER_DIR)/fifo-dlq-handler/assets/requirements.txt
	cd $(APPLICATION_DIR)/fifo_dlq_handler
	tar -czf $(DOCKER_DIR)/fifo-dlq-handler/assets/fifo-dlq-handler-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=fifo-dlq-handler AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make fifo-dlq-handler-clean
	export VERSION=$$(make docker-image-get-version NAME=fifo-dlq-handler)

fifo-dlq-handler-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/fifo-dlq-handler/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/fifo-dlq-handler/assets/*.txt
	make common-code-remove LAMBDA_DIR=fifo_dlq_handler

# ==============================================================================
# Authoriser (for dos api gateway mock)

authoriser-build-and-push: ### Build authoriser lambda docker image
	cp -f $(APPLICATION_DIR)/authoriser/requirements.txt $(DOCKER_DIR)/authoriser/assets/requirements.txt
	cd $(APPLICATION_DIR)/authoriser
	tar -czf $(DOCKER_DIR)/authoriser/assets/authoriser-app.tar.gz \
		--exclude=tests \
		*.py
	cd $(PROJECT_DIR)
	make docker-image NAME=authoriser AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make authoriser-clean
	make docker-push NAME=authoriser AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

authoriser-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/authoriser/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/authoriser/assets/*.txt

# ==============================================================================
# DoS API Gateway Mock lambda

dos-api-gateway-build-and-push:
	cp -f $(APPLICATION_DIR)/dos_api_gateway/requirements.txt $(DOCKER_DIR)/dos-api-gateway/assets/requirements.txt
	cd $(APPLICATION_DIR)/dos_api_gateway
	tar -czf $(DOCKER_DIR)/dos-api-gateway/assets/dos-api-gateway-app.tar.gz \
		--exclude=tests \
		*.py
	cd $(PROJECT_DIR)
	make docker-image NAME=dos-api-gateway AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make dos-api-gateway-clean
	make docker-push NAME=dos-api-gateway AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

dos-api-gateway-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/dos-api-gateway/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/dos-api-gateway/assets/*.txt

# ==============================================================================
# Deployments

sls-only-deploy: # Deploys all lambdas - mandatory: PROFILE, VERSION=[commit hash-timestamp]
	eval "$$(make -s populate-deployment-variables)"
	make serverless-deploy

quick-build-and-deploy: # Build and deploy lambdas only (meant to for fast redeployment of existing lambdas) - mandatory: PROFILE
	make -s build VERSION=$(BUILD_TAG)
	make -s push-images VERSION=$(BUILD_TAG)
	make -s sls-only-deploy VERSION=$(BUILD_TAG)

# ==============================================================================
# Serverless

push-tester-image:
	make docker-push NAME=tester

push-images: # Use VERSION=[] to push a perticular version otherwise with default to latest
	make docker-push NAME=event-sender AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make docker-push NAME=event-processor AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)
	make docker-push NAME=fifo-dlq-handler AWS_ACCOUNT_ID_MGMT=$(AWS_ACCOUNT_ID_NONPROD)

serverless-requirements: # Install serverless plugins
	make serverless-install-plugin NAME="serverless-vpc-discovery"
	make serverless-install-plugin NAME="serverless-localstack"

# ==============================================================================
# Pipelines

deploy-development-pipeline:
	make terraform-apply-auto-approve STACKS=development-pipeline

undeploy-development-pipeline:
	make terraform-destroy-auto-approve STACKS=development-pipeline

plan-development-pipeline:
	if [ "$(PROFILE)" == "dev" ]; then
		export TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-plan STACKS=development-pipeline
	fi
	if [ "$(PROFILE)" != "dev" ]; then
		echo "Only dev profile supported at present"
	fi

docker-hub-signin: # Sign into Docker hub
	export DOCKER_USERNAME=$$($(AWSCLI) secretsmanager get-secret-value --secret-id uec-pu-updater/deployment --version-stage AWSCURRENT --region $(AWS_REGION) --query '{SecretString: SecretString}' | jq --raw-output '.SecretString' | jq -r .DOCKER_HUB_USERNAME)
	export DOCKER_PASSWORD=$$($(AWSCLI) secretsmanager get-secret-value --secret-id uec-pu-updater/deployment --version-stage AWSCURRENT --region $(AWS_REGION) --query '{SecretString: SecretString}' | jq --raw-output '.SecretString' | jq -r .DOCKER_HUB_PASS)
	make docker-login

# ==============================================================================
# Tester

tester-build: ### Build tester docker image
	cp -f $(APPLICATION_DIR)/requirements-dev.txt $(DOCKER_DIR)/tester/assets/
	cp -f $(APPLICATION_DIR)/event_processor/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-processor.txt
	cp -f $(APPLICATION_DIR)/event_sender/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-sender.txt
	cp -f $(APPLICATION_DIR)/fifo_dlq_handler/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-fifo-dlq-hander.txt
	cat build/docker/tester/assets/requirements*.txt | sort --unique >> $(DOCKER_DIR)/tester/assets/requirements.txt
	rm -f $(DOCKER_DIR)/tester/assets/requirements-*.txt
	make docker-image NAME=tester
	make tester-clean

tester-clean:
	rm -fv $(DOCKER_DIR)/tester/assets/*.txt

# ==============================================================================
# Testing

# -----------------------------
# Performance Testing

performance-test:
	TIME_DATE=$$(date +%Y-%m-%d_%H-%M-%S)
	make -s docker-run-tools \
		IMAGE=$$(make _docker-get-reg)/tester \
		CMD="python -m locust -f locustfile.py --headless \
			--users 10 --spawn-rate 1 --run-time 30s \
			-H https://$(DOS_INTEGRATION_URL) --stop-timeout 99 \
			--csv=results/$$TIME_DATE" \
		DIR=./test/performance \
		ARGS="\
			-p 8089:8089 \
			-e API_KEY_SECRET_NAME=$(TF_VAR_api_gateway_api_key_name) \
			-e API_KEY_SECRET_KEY=$(TF_VAR_nhs_uk_api_key_key)"

# -----------------------------
# Other

python-linting:
	make python-code-check FILES=application
	make python-code-check FILES=test

create-ecr-repositories:
	make docker-create-repository NAME=event-processor
	make docker-create-repository NAME=event-sender
	make docker-create-repository NAME=fifo-dlq-handler
