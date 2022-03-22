PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: project-config # Set up project
	make docker-build NAME=serverless
	make tester-build
	make mock-dos-db-setup

build: # Build lambdas
	make -s event-sender-build \
		event-processor-build \
		fifo-dlq-handler-build \
		cr-fifo-dlq-handler-build \
		orchestrator-build \
		event-replay-build \
		authoriser-build \
		dos-api-gateway-build \
		test-db-checker-handler-build

start: # Stop project
	make project-start

stop: # Stop project
	make project-stop

restart: stop start # Restart project

log: project-log # Show project logs

deploy: # Deploys whole project - mandatory: PROFILE
	make -s terraform-clean
	if [ "$(PROFILE)" == "task" ] || [ "$(PROFILE)" == "dev" ] || [ "$(PROFILE)" == "perf" ]; then
		make mock-dos-api-gateway-deployment
	fi
	eval "$$(make -s populate-deployment-variables)"
	make terraform-apply-auto-approve STACKS=api-key,lambda-security-group,lambda-iam-roles,dynamo-db
	make serverless-deploy
	make terraform-apply-auto-approve STACKS=api-gateway-sqs,splunk-logs,cloudwatch-dashboard

undeploy: # Undeploys whole project - mandatory: PROFILE
	eval "$$(make -s populate-deployment-variables)"
	make terraform-destroy-auto-approve STACKS=splunk-logs,api-gateway-sqs,cloudwatch-dashboard
	make serverless-remove VERSION="any" DB_PASSWORD="any"
	make terraform-destroy-auto-approve STACKS=lambda-security-group,lambda-iam-roles
	if [ "$(PROFILE)" == "task" ] || [ "$(PROFILE)" == "dev" ]; then
		make terraform-destroy-auto-approve STACKS=dos-api-gateway-mock
		make terraform-destroy-auto-approve STACKS=dynamo-db OPTS="-refresh=false"
	fi

build-and-deploy: # Builds and Deploys whole project - mandatory: PROFILE
	make build VERSION=$(BUILD_TAG)
	make push-images VERSION=$(BUILD_TAG)
	make deploy VERSION=$(BUILD_TAG)

populate-deployment-variables:
	eval "$$(make aws-assume-role-export-variables)"
	echo "export DB_SERVER=$$(make -s aws-rds-describe-instance-value DB_INSTANCE=$(DB_SERVER_NAME) KEY_DOT_PATH=Endpoint.Address)"
	echo "export DB_USER_NAME=$$(make -s secret-get-existing-value NAME=$(DB_USER_NAME_SECRET_NAME) KEY=$(DB_USER_NAME_SECRET_KEY))"

unit-test-local:
	pyenv local .venv
	pip install -r application/requirements-dev.txt -r application/event_processor/requirements.txt -r application/event_replay/requirements.txt -r application/event_sender/requirements.txt -r application/fifo_dlq_handler/requirements.txt
	cd application
	python -m pytest --junitxml=./testresults.xml --cov=. -vv

unit-test:
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	CMD="python -m pytest --junitxml=./testresults.xml --cov-report term-missing  --cov-report xml:coverage.xml --cov=. -vv" \
	DIR=./application \
	ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/authoriser:/tmp/.packages/authoriser \
		--volume $(APPLICATION_DIR)/dos_api_gateway:/tmp/.packages/dos_api_gateway \
		--volume $(APPLICATION_DIR)/event_processor:/tmp/.packages/event_processor \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		--volume $(APPLICATION_DIR)/fifo_dlq_handler:/tmp/.packages/fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/cr_fifo_dlq_handler:/tmp/.packages/cr_fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/event_replay:/tmp/.packages/event_replay \
		--volume $(APPLICATION_DIR)/test_db_checker_handler:/tmp/.packages/test_db_checker_handler \
		--volume $(APPLICATION_DIR)/orchestrator:/tmp/.packages/orchestrator \
		"

coverage-report: # Runs whole project coverage unit tests
	make -s python-code-coverage DIR=$(APPLICATION_DIR_REL) \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/authoriser:/tmp/.packages/authoriser \
		--volume $(APPLICATION_DIR)/dos_api_gateway:/tmp/.packages/dos_api_gateway \
		--volume $(APPLICATION_DIR)/event_processor:/tmp/.packages/event_processor \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		--volume $(APPLICATION_DIR)/fifo_dlq_handler:/tmp/.packages/fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/cr_fifo_dlq_handler:/tmp/.packages/cr_fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/event_replay:/tmp/.packages/event_replay \
		--volume $(APPLICATION_DIR)/test_db_checker_handler:/tmp/.packages/test_db_checker_handler \
		--volume $(APPLICATION_DIR)/orchestrator:/tmp/.packages/orchestrator \
		"

smoke-test: #Integration Smoke test for DI project - mandatory: PROFILE, ENVIRONMENT=test
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	CMD="pytest steps -k smoke -vv --gherkin-terminal-reporter -p no:sugar -n auto --cucumberjson=./testresults.json --disable-pytest-warnings" \
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
		-e TEST_DB_CHECKER_FUNCTION_NAME=$(TF_VAR_test_db_checker_lambda_name) \
		-e EVENT_REPLAY=$(TF_VAR_event_replay_lambda_name) \
		-e DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
		-e DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
		-e RUN_ID=${RUN_ID} \
		-e CR_FIFO_DLQ=$(TF_VAR_cr_fifo_dlq_handler_lambda_name) \
		"

integration-test-local:
	cd test/integration
	API_KEY_SECRET=$(TF_VAR_api_gateway_api_key_name) \
	NHS_UK_API_KEY=$(TF_VAR_nhs_uk_api_key_key) \
	DOS_DB_PASSWORD_SECRET_NAME=$(DB_SECRET_NAME) \
	DOS_DB_PASSWORD_KEY=$(DB_SECRET_KEY) \
	DOS_DB_USERNAME_SECRET_NAME=$(DB_USER_NAME_SECRET_NAME) \
	DOS_DB_USERNAME_KEY=$(DB_USER_NAME_SECRET_KEY) \
	URL=https://$(DOS_INTEGRATION_URL) \
	EVENT_PROCESSOR=$(TF_VAR_event_processor_lambda_name) \
	EVENT_SENDER=$(TF_VAR_event_sender_lambda_name) \
	SQS_URL=$(SQS_QUEUE_URL) \
	TEST_DB_CHECKER_FUNCTION_NAME=$(TF_VAR_test_db_checker_lambda_name) \
	EVENT_REPLAY=$(TF_VAR_event_replay_lambda_name) \
	DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
	DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
	KEYALIAS=${TF_VAR_signing_key_alias} \
	RUN_ID=${RUN_ID} \
	pytest steps -k $(TAGS) -vv --gherkin-terminal-reporter -p no:sugar -n 8 --cucumberjson=./testresults.json

integration-test: #End to end test DI project - mandatory: PROFILE, TAGS=[complete|dev]; optional: ENVIRONMENT, PARALLEL_TEST_COUNT
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	CMD="pytest steps -k $(TAGS) -vv --gherkin-terminal-reporter -p no:sugar -n $(PARALLEL_TEST_COUNT) --cucumberjson=./testresults.json" \
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
		-e TEST_DB_CHECKER_FUNCTION_NAME=$(TF_VAR_test_db_checker_lambda_name) \
		-e EVENT_REPLAY=$(TF_VAR_event_replay_lambda_name) \
		-e SQS_URL=$(SQS_QUEUE_URL) \
		-e DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
		-e DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
		-e RUN_ID=${RUN_ID} \
		-e CR_FIFO_DLQ=$(TF_VAR_cr_fifo_dlq_handler_lambda_name) \
		"

clean: # Runs whole project clean
	make \
		docker-clean \
		terraform-clean \
		serverless-clean \
		python-clean \
		event-sender-clean \
		event-processor-clean \
		fifo-dlq-handler-clean \
		cr-fifo-dlq-handler-clean \
		event-replay-clean \
		test-db-checker-handler-clean \
		tester-clean \
		authoriser-clean \
		dos-api-gateway-clean \
		performance-test-clean

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
	make docker-image NAME=event-sender
	make event-sender-clean
	export VERSION=$$(make docker-image-get-version NAME=event-sender)

event-sender-clean: ### Clean event sender lambda docker image directory
	rm -fv $(DOCKER_DIR)/event-sender/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/event-sender/assets/*.txt
	make common-code-remove LAMBDA_DIR=event_sender

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
	make docker-image NAME=event-processor
	make event-processor-clean
	export VERSION=$$(make docker-image-get-version NAME=event-processor)

event-processor-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/event-processor/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/event-processor/assets/*.txt
	make common-code-remove LAMBDA_DIR=event_processor

# ==============================================================================
# First In First Out Dead Letter Queue Handler (fifo-dlq-handler)

fifo-dlq-handler-build: ### Build fifo dlq handler lambda docker image
	make common-code-copy LAMBDA_DIR=fifo_dlq_handler
	cp -f $(APPLICATION_DIR)/fifo_dlq_handler/requirements.txt $(DOCKER_DIR)/fifo-dlq-handler/assets/requirements.txt
	cd $(APPLICATION_DIR)/fifo_dlq_handler
	tar -czf $(DOCKER_DIR)/fifo-dlq-handler/assets/fifo-dlq-handler-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=fifo-dlq-handler
	make fifo-dlq-handler-clean
	export VERSION=$$(make docker-image-get-version NAME=fifo-dlq-handler)

fifo-dlq-handler-clean: ### Clean fifo dlq handler lambda docker image directory
	rm -fv $(DOCKER_DIR)/fifo-dlq-handler/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/fifo-dlq-handler/assets/*.txt
	make common-code-remove LAMBDA_DIR=fifo_dlq_handler

# ==============================================================================
# CR Fifo Dead Letter Queue Handler (cr-fifo-dlq-handler)

cr-fifo-dlq-handler-build: ### Build cr-fifo dlq handler lambda docker image
	make common-code-copy LAMBDA_DIR=cr_fifo_dlq_handler
	cp -f $(APPLICATION_DIR)/cr_fifo_dlq_handler/requirements.txt $(DOCKER_DIR)/cr-fifo-dlq-handler/assets/requirements.txt
	cd $(APPLICATION_DIR)/cr_fifo_dlq_handler
	tar -czf $(DOCKER_DIR)/cr-fifo-dlq-handler/assets/cr-fifo-dlq-handler-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=cr-fifo-dlq-handler
	make cr-fifo-dlq-handler-clean
	export VERSION=$$(make docker-image-get-version NAME=cr-fifo-dlq-handler)

cr-fifo-dlq-handler-clean: ### Clean cr-fifo dlq handler lambda docker image directory
	rm -fv $(DOCKER_DIR)/cr-fifo-dlq-handler/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/cr-fifo-dlq-handler/assets/*.txt
	make common-code-remove LAMBDA_DIR=cr_fifo_dlq_handler

# ==============================================================================
# Event Replay lambda (event-replay)

event-replay-build: ### Build event replay lambda docker image
	make common-code-copy LAMBDA_DIR=event_replay
	cp -f $(APPLICATION_DIR)/event_replay/requirements.txt $(DOCKER_DIR)/event-replay/assets/requirements.txt
	cd $(APPLICATION_DIR)/event_replay
	tar -czf $(DOCKER_DIR)/event-replay/assets/event-replay-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=event-replay
	make event-replay-clean
	export VERSION=$$(make docker-image-get-version NAME=event-replay)

event-replay-clean: ### Clean event replay lambda docker image directory
	rm -fv $(DOCKER_DIR)/event-replay/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/event-replay/assets/*.txt
	make common-code-remove LAMBDA_DIR=event_replay

# ==============================================================================
# Test DB Checker Handler (test-db-checker-handler)

test-db-checker-handler-build: ### Build event processor lambda docker image
	make common-code-copy LAMBDA_DIR=test_db_checker_handler
	cp -f $(APPLICATION_DIR)/test_db_checker_handler/requirements.txt $(DOCKER_DIR)/test-db-checker-handler/assets/requirements.txt
	cd $(APPLICATION_DIR)/test_db_checker_handler
	tar -czf $(DOCKER_DIR)/test-db-checker-handler/assets/test-db-checker-handler-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make docker-image NAME=test-db-checker-handler
	make test-db-checker-handler-clean
	export VERSION=$$(make docker-image-get-version NAME=test-db-checker-handler)

test-db-checker-handler-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/test-db-checkerhandler/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/test-db-checker-handler/assets/*.txt
	make common-code-remove LAMBDA_DIR=test_db_checker_handler

# ==============================================================================
# Orchestrator

orchestrator-build: ### Build orchestrator lambda docker image
	make common-code-copy LAMBDA_DIR=orchestrator
	cp -f $(APPLICATION_DIR)/orchestrator/requirements.txt $(DOCKER_DIR)/orchestrator/assets/requirements.txt
	cd $(APPLICATION_DIR)/orchestrator
	tar -czf $(DOCKER_DIR)/orchestrator/assets/orchestrator-app.tar.gz \
		--exclude=tests \
		*.py \
		common
	cd $(PROJECT_DIR)
	make -s docker-image NAME=orchestrator
	make orchestrator-clean
	export VERSION=$$(make docker-image-get-version NAME=orchestrator)

orchestrator-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/orchestrator/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/orchestrator/assets/*.txt
	make common-code-remove LAMBDA_DIR=orchestrator

# ==============================================================================
# Authoriser (for dos api gateway mock)

authoriser-build: ### Build authoriser lambda docker image
	cp -f $(APPLICATION_DIR)/authoriser/requirements.txt $(DOCKER_DIR)/authoriser/assets/requirements.txt
	cd $(APPLICATION_DIR)/authoriser
	tar -czf $(DOCKER_DIR)/authoriser/assets/authoriser-app.tar.gz \
		--exclude=tests \
		*.py
	cd $(PROJECT_DIR)
	make -s docker-image NAME=authoriser
	make authoriser-clean
	export VERSION=$$(make docker-image-get-version NAME=authoriser)

authoriser-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/authoriser/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/authoriser/assets/*.txt

# ==============================================================================
# DoS API Gateway Mock lambda

dos-api-gateway-build:
	cp -f $(APPLICATION_DIR)/dos_api_gateway/requirements.txt $(DOCKER_DIR)/dos-api-gateway/assets/requirements.txt
	cd $(APPLICATION_DIR)/dos_api_gateway
	tar -czf $(DOCKER_DIR)/dos-api-gateway/assets/dos-api-gateway-app.tar.gz \
		--exclude=tests \
		*.py
	cd $(PROJECT_DIR)
	make -s docker-image NAME=dos-api-gateway
	make dos-api-gateway-clean
	export VERSION=$$(make docker-image-get-version NAME=dos-api-gateway)

dos-api-gateway-clean: ### Clean event processor lambda docker image directory
	rm -fv $(DOCKER_DIR)/dos-api-gateway/assets/*.tar.gz
	rm -fv $(DOCKER_DIR)/dos-api-gateway/assets/*.txt

build-and-push-mock-dos-api-gateway-docker-images:
	make authoriser-build dos-api-gateway-build
	make docker-push NAME=authoriser
	make docker-push NAME=dos-api-gateway

mock-dos-api-gateway-deployment:
	make terraform-apply-auto-approve STACKS=dos-api-gateway-mock

# ==============================================================================
# Deployments

sls-only-deploy: # Deploys all lambdas - mandatory: PROFILE, VERSION=[commit hash-timestamp]
	eval "$$(make -s populate-deployment-variables)"
	make serverless-deploy

quick-build-and-deploy: # Build and deploy lambdas only (meant to for fast redeployment of existing lambdas) - mandatory: PROFILE
	make -s build VERSION=$(BUILD_TAG)
	make -s push-images VERSION=$(BUILD_TAG)
	make -s sls-only-deploy VERSION=$(BUILD_TAG)

push-images: # Use VERSION=[] to push a perticular version otherwise with default to latest
	make docker-push NAME=event-sender
	make docker-push NAME=event-processor
	make docker-push NAME=fifo-dlq-handler
	make docker-push NAME=cr-fifo-dlq-handler
	make docker-push NAME=event-replay
	make docker-push NAME=test-db-checker-handler
	make docker-push NAME=orchestrator
	make docker-push NAME=authoriser
	make docker-push NAME=dos-api-gateway

push-tester-image:
	make docker-push NAME=tester

# ==============================================================================
# Pipelines

deploy-development-pipeline:
	make terraform-apply-auto-approve STACKS=development-pipeline PROFILE=tools

undeploy-development-pipeline:
	make terraform-destroy-auto-approve STACKS=development-pipeline PROFILE=tools

plan-development-pipeline:
	if [ "$(PROFILE)" == "tools" ]; then
		export TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-plan STACKS=development-pipeline
	else
		echo "Only tools profile supported at present"
	fi

deploy-deployment-pipelines:
	if [ "$(PROFILE)" == "tools" ] && [ "$(ENVIRONMENT)" == "dev" ]; then
		TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-apply-auto-approve STACKS=deployment-pipelines TF_VAR_github_token=$$TF_VAR_github_token
	else
		echo "PROFILE must be tools and ENVIRONMENT must be dev"
	fi

undeploy-deployment-pipelines:
	if [ "$(PROFILE)" == "tools" ] && [ "$(ENVIRONMENT)" == "dev" ]; then
		TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-destroy-auto-approve STACKS=deployment-pipelines TF_VAR_github_token=$$TF_VAR_github_token
	else
		echo "PROFILE must be tools and ENVIRONMENT must be dev"
	fi

plan-deployment-pipelines:
	if [ "$(PROFILE)" == "tools" ] && [ "$(ENVIRONMENT)" == "dev" ]; then
		TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-plan STACKS=deployment-pipelines TF_VAR_github_token=$$TF_VAR_github_token
	else
		echo "PROFILE must be tools and ENVIRONMENT must be dev"
	fi

deploy-performance-pipelines:
	make terraform-apply-auto-approve STACKS=performance-pipelines PROFILE=dev

undeploy-performance-pipelines:
	make terraform-destroy-auto-approve STACKS=performance-pipelines PROFILE=dev

plan-performance-pipelines:
	if [ "$(PROFILE)" == "dev" ]; then
		export TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-plan STACKS=performance-pipelines
	else
		echo "Only dev profile supported at present"
	fi

docker-hub-signin: # Sign into Docker hub
	export DOCKER_USERNAME=$$($(AWSCLI) secretsmanager get-secret-value --secret-id uec-pu-updater/deployment --version-stage AWSCURRENT --region $(AWS_REGION) --query '{SecretString: SecretString}' | jq --raw-output '.SecretString' | jq -r .DOCKER_HUB_USERNAME)
	export DOCKER_PASSWORD=$$($(AWSCLI) secretsmanager get-secret-value --secret-id uec-pu-updater/deployment --version-stage AWSCURRENT --region $(AWS_REGION) --query '{SecretString: SecretString}' | jq --raw-output '.SecretString' | jq -r .DOCKER_HUB_PASS)
	make docker-login

wait-for-codebuild-to-finish: # Wait for codebuild project to finish
	build_id=$$(aws codebuild list-builds-for-project --project-name $(PROJECT_NAME) --sort-order DESCENDING | jq --raw-output '.ids[0]')
	while [[ $$(aws codebuild batch-get-builds --ids $$build_id | jq --raw-output '.builds[0].buildStatus') == "IN_PROGRESS" ]]; do
		echo Waiting for $(PROJECT_NAME) to finish
		sleep 60
	done

tag-commit-for-deployment: # Tag git commit for deployment - mandatory: PROFILE=[demo/live], COMMIT=[short commit hash]
	if [ "$(PROFILE)" == "$(ENVIRONMENT)" ]; then
		make git-tag-create-environment-deployment COMMIT=$(COMMIT)
	else
		echo PROFILE=$(PROFILE) should equal ENVIRONMENT=$(ENVIRONMENT)
		echo Recommended: you run this command from the master branch
	fi

tag-commit-to-destroy-environment: # Tag git commit to destroy deployment - mandatory: ENVIRONMENT=[di-number], COMMIT=[short commit hash]
	if [ "$(PROFILE)" != "$(ENVIRONMENT)" ]; then
		tag=$(ENVIRONMENT)-destroy-$(BUILD_TIMESTAMP)
		make git-tag-create TAG=$$tag COMMIT=$(COMMIT)
	else
		echo This is for destroying old task environments PROFILE should not be equal to ENVIRONMENT
	fi

# ==============================================================================
# Tester

tester-build: ### Build tester docker image
	cp -f $(APPLICATION_DIR)/requirements-dev.txt $(DOCKER_DIR)/tester/assets/
	cp -f $(APPLICATION_DIR)/event_processor/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-processor.txt
	cp -f $(APPLICATION_DIR)/event_sender/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-sender.txt
	cp -f $(APPLICATION_DIR)/fifo_dlq_handler/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-fifo-dlq-hander.txt
	cp -f $(APPLICATION_DIR)/cr_fifo_dlq_handler/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-cr-fifo-dlq-hander.txt
	cp -f $(APPLICATION_DIR)/event_replay/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-event-replay.txt
	cp -f $(APPLICATION_DIR)/test_db_checker_handler/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-test-db-checker-handler.txt
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

stress-test: # Create change events for stress performance testing - mandatory: PROFILE, ENVIRONMENT, START_TIME=[timestamp], optional: PIPELINE=true/false
	if [ $(PIPELINE) == true ]; then
		PERFORMANCE_ARGS=$$(echo --users 5 --spawn-rate 5 --run-time 30s)
	else
		PERFORMANCE_ARGS=$$(echo --users 10 --spawn-rate 2 --run-time 10m)
	fi
	make -s docker-run-tools \
		IMAGE=$$(make _docker-get-reg)/tester \
		CMD="python -m locust -f stress_test_locustfile.py --headless \
			$$PERFORMANCE_ARGS --stop-timeout 10 --exit-code-on-error 0 \
			-H https://$(DOS_INTEGRATION_URL) \
			--csv=results/$(START_TIME)_create_change_events" \
		DIR=./test/performance/create_change_events \
		ARGS="\
			-p 8089:8089 \
			-e API_KEY_SECRET_NAME=$(TF_VAR_api_gateway_api_key_name) \
			-e API_KEY_SECRET_KEY=$(TF_VAR_nhs_uk_api_key_key) \
			-e CHANGE_EVENTS_TABLE_NAME=$(TF_VAR_change_events_table_name) \
			"

load-test: # Create change events for load performance testing - mandatory: PROFILE, ENVIRONMENT, START_TIME=[timestamp]
	make -s docker-run-tools \
		IMAGE=$$(make _docker-get-reg)/tester \
		CMD="python -m locust -f load_test_locustfile.py --headless \
			--users 50 --spawn-rate 2 --run-time 30m --stop-timeout 5	 --exit-code-on-error 0 \
			-H https://$(DOS_INTEGRATION_URL) \
			--csv=results/$(START_TIME)_create_change_events" \
		DIR=./test/performance/create_change_events \
		ARGS="\
			-p 8089:8089 \
			-e API_KEY_SECRET_NAME=$(TF_VAR_api_gateway_api_key_name) \
			-e API_KEY_SECRET_KEY=$(TF_VAR_nhs_uk_api_key_key) \
			-e CHANGE_EVENTS_TABLE_NAME=$(TF_VAR_change_events_table_name) \
			"

performance-test-data-collection: # Runs data collection for performance tests - mandatory: PROFILE, ENVIRONMENT, START_TIME=[timestamp], END_TIME=[timestamp]
	make -s docker-run-tools \
		IMAGE=$$(make _docker-get-reg)/tester \
		CMD="python data_collection.py" \
		DIR=./test/performance/data_collection \
		ARGS="\
			-e START_TIME=$(START_TIME) \
			-e END_TIME=$(END_TIME) \
			-e FIFO_QUEUE_NAME=$(TF_VAR_fifo_queue_name) \
			-e FIFO_DLQ_NAME=$(TF_VAR_dead_letter_queue_from_fifo_queue_name) \
			-e EVENT_SENDER_NAME=$(TF_VAR_event_sender_lambda_name) \
			-e EVENT_PROCESSOR_NAME=$(TF_VAR_event_processor_lambda_name) \
			-e RDS_INSTANCE_IDENTIFIER=$(DB_SERVER_NAME) \
			"

generate-performance-test-details: # Generates performance test details - mandatory: PROFILE, ENVIRONMENT, START_TIME=[timestamp], END_TIME=[timestamp], TEST_TYPE="string", CODE_VERSION="string"
	rm -rf $(TMP_DIR)/performance
	mkdir $(TMP_DIR)/performance
	echo -e "PROFILE=$(PROFILE)\nENVIRONMENT=$(ENVIRONMENT)\nTEST_TYPE=$(TEST_TYPE)\nCODE_VERSION=$(CODE_VERSION)\nSTART_TIME=$(START_TIME)\nEND_TIME=$(END_TIME)" > $(TMP_DIR)/performance/test_details.txt
	cp test/performance/create_change_events/results/$(START_TIME)* $(TMP_DIR)/performance
	cp test/performance/data_collection/results/$(START_TIME)* $(TMP_DIR)/performance
	zip -r $(TMP_DIR)/$(START_TIME)-$(ENVIRONMENT)-performance-tests.zip $(TMP_DIR)/performance
	aws s3 cp $(TMP_DIR)/$(START_TIME)-$(ENVIRONMENT)-performance-tests.zip s3://uec-dos-int-performance-tests-nonprod/$(START_TIME)-$(ENVIRONMENT)-performance-tests.zip

performance-test-clean: # Clean up performance test results
	rm -rf $(TMP_DIR)/performance
	rm -f $(TMP_DIR)/*.zip
	rm -rf $(PROJECT_DIR)/test/performance/create_change_events/results/*.csv
	rm -rf $(PROJECT_DIR)/test/performance/data_collection/results/*.csv

stress-test-in-pipeline: # An all in one stress test make target
	START_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_START_TIME=$$(date +%FT%TZ)
	CODE_VERSION=$$($(AWSCLI) lambda get-function --function-name $(TF_VAR_event_processor_lambda_name) | jq --raw-output '.Configuration.Environment.Variables.CODE_VERSION')
	make stress-test START_TIME=$$START_TIME PIPELINE=true
	sleep 4.5h
	END_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_END_TIME=$$(date +%FT%TZ)
	make performance-test-data-collection START_TIME=$$START_TIME END_TIME=$$END_TIME
	make generate-performance-test-details START_TIME=$$START_TIME END_TIME=$$END_TIME TEST_TYPE="stress test" CODE_VERSION=$$CODE_VERSION
	make send-performance-dashboard-slack-message START_DATE_TIME=$$AWS_START_TIME END_DATE_TIME=$$AWS_END_TIME

load-test-in-pipeline: # An all in one load test make target
	START_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_START_TIME=$$(date +%FT%TZ)
	CODE_VERSION=$$($(AWSCLI) lambda get-function --function-name $(TF_VAR_event_processor_lambda_name) | jq --raw-output '.Configuration.Environment.Variables.CODE_VERSION')
	make load-test START_TIME=$$START_TIME
	sleep 10m
	END_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_END_TIME=$$(date +%FT%TZ)
	make performance-test-data-collection START_TIME=$$START_TIME END_TIME=$$END_TIME
	make generate-performance-test-details START_TIME=$$START_TIME END_TIME=$$END_TIME TEST_TYPE="load test" CODE_VERSION=$$CODE_VERSION
	make send-performance-dashboard-slack-message START_DATE_TIME=$$AWS_START_TIME END_DATE_TIME=$$AWS_END_TIME

send-performance-dashboard-slack-message:
	aws sns publish --topic-arn arn:aws:sns:$(AWS_REGION):$(AWS_ACCOUNT_ID_NONPROD):uec-dos-int-dev-pipeline-topic --message '{
	"version": "0",
	"id": "13cde686-328b-6117-af20-0e5566167482",
	"detail-type": "Performance Dashboard Here - https://$(AWS_REGION).console.aws.amazon.com/cloudwatch/home?region=$(AWS_REGION)#dashboards:name=$(TF_VAR_cloudwatch_monitoring_dashboard_name);start=$(START_DATE_TIME);end=$(END_DATE_TIME)",
	"source": "aws.ecr",
	"account": "$(AWS_ACCOUNT_ID_NONPROD)",
	"time": "2019-11-16T01:54:34Z",
	"region": "$(AWS_REGION)",
	"resources": [],
	"detail": {}
	}'

# -----------------------------
# Chaos Testing

setup-no-dos-chaos-test: # Setup chaos test environment (Sets DoS API Gateway mock to be unavailable) - mandatory: PROFILE; optional: ENVIRONMENT
	make terraform-destroy-auto-approve STACKS="dos-api-gateway-mock" OPTS="-target aws_route53_record.uec_dos_integration_api_endpoint"

restore-from-no-dos-chaos-test: # Restore from chaos test environment - mandatory: PROFILE; optional: ENVIRONMENT
	VERSION=$$(echo $(BUILD_TAG))
	make build-and-push-mock-dos-api-gateway-docker-images VERSION=$$VERSION
	make mock-dos-api-gateway-deployment VERSION=$$VERSION

setup-circuit-breaker-chaos-test: # Setup chaos test environment (Sets DoS API Gateway mock to return 500 errors) - mandatory: PROFILE; optional: ENVIRONMENT
	VERSION=$$(echo $(BUILD_TAG))
	make build-and-push-mock-dos-api-gateway-docker-images VERSION=$$VERSION
	make mock-dos-api-gateway-deployment VERSION=$$VERSION TF_VAR_chaos_mode="true"

restore-from-circuit-breaker-chaos-test: # Restore from chaos test environment - mandatory: PROFILE; optional: ENVIRONMENT
	VERSION=$$(echo $(BUILD_TAG))
	make build-and-push-mock-dos-api-gateway-docker-images VERSION=$$VERSION
	make mock-dos-api-gateway-deployment VERSION=$$VERSION

# -----------------------------
# Other

update-all-ip-allowlists: # Update your IP address in AWS secrets manager to acesss non-prod environments - mandatory: PROFILE, ENVIRONMENT, USERNAME
	USERNAME=$$(git config user.name)
	make -s update-ip-allowlist PROFILE=task USERNAME="$$USERNAME"
	make -s update-ip-allowlist PROFILE=dev USERNAME="$$USERNAME"

update-ip-allowlist: # Update your IP address in AWS secrets manager to acesss non-prod environments - mandatory: PROFILE, ENVIRONMENT, USERNAME
	make -s docker-run-python \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		CMD="python update-ip-address.py $(USERNAME)" \
		DIR=$(BIN_DIR) ARGS="-e IP_SECRET=$(TF_VAR_ip_address_secret)"

update-ip-allowlists-and-deploy-allowlist: # Update your IP address in AWS secrets manager to acesss non-prod environments and then redeploy environment - mandatory: PROFILE, ENVIRONMENT
	make update-all-ip-allowlists
	make -s terraform-clean
	make -s terraform-apply-auto-approve STACKS=api-gateway-sqs

delete-ip-from-allowlist: # Update your IP address in AWS secrets manager to acesss test environment - mandatory: PROFILE, ENVIRONMENT, USERNAME
	make -s docker-run-python \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		CMD="python delete-ip-address.py $(USERNAME)" \
		DIR=$(BIN_DIR) ARGS="-e IP_SECRET=$(TF_VAR_ip_address_secret)"

python-linting:
	make python-code-check FILES=application
	make python-code-check FILES=test

python-format:
	make python-code-format FILES=application
	make python-code-format FILES=test

create-ecr-repositories:
	make docker-create-repository NAME=event-processor
	make docker-create-repository NAME=event-sender
	make docker-create-repository NAME=fifo-dlq-handler
	make docker-create-repository NAME=cr-fifo-dlq-handler
	make docker-create-repository NAME=orchestrator
	make docker-create-repository NAME=event-replay
	make docker-create-repository NAME=slack-messenger
	make docker-create-repository NAME=test-db-checker-handler
	make docker-create-repository NAME=tester
