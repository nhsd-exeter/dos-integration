PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: project-config # Set up project
	make serverless-build
	make tester-build

build: # Build lambdas
	make -s event-sender-build \
		event-processor-build \
		fifo-dlq-handler-build \
		cr-fifo-dlq-handler-build \
		orchestrator-build \
		slack-messenger-build \
		authoriser-build \
		dos-api-gateway-build \
		event-replay-build \
		test-db-checker-handler-build

start: # Stop project
	make project-start

stop: # Stop project
	make project-stop

restart: stop start # Restart project

log: project-log # Show project logs

deploy: # Deploys whole project - mandatory: PROFILE
	if [ "$(PROFILE)" == "task" ] || [ "$(PROFILE)" == "dev" ] || [ "$(PROFILE)" == "perf" ]; then
		make mock-dos-api-gateway-deployment
	fi
	eval "$$(make -s populate-deployment-variables)"
	make terraform-apply-auto-approve STACKS=api-key,appconfig,before-lambda-deployment
	make serverless-deploy
	make terraform-apply-auto-approve STACKS=after-lambda-deployment

undeploy: # Undeploys whole project - mandatory: PROFILE
	make terraform-destroy-auto-approve STACKS=after-lambda-deployment
	make serverless-remove VERSION="any" DB_PASSWORD="any" DB_SERVER="any" DB_USER_NAME="any" SLACK_WEBHOOK_URL="any"
	make terraform-destroy-auto-approve STACKS=before-lambda-deployment,appconfig
	if [ "$(PROFILE)" == "task" ] || [ "$(PROFILE)" == "dev" ] || [ "$(PROFILE)" == "perf" ]; then
		make terraform-destroy-auto-approve STACKS=api-key
	fi
	if [ "$(PROFILE)" == "task" ] || [ "$(PROFILE)" == "dev" ] || [ "$(PROFILE)" == "perf" ]; then
		make terraform-destroy-auto-approve STACKS=dos-api-gateway-mock
	fi

build-and-deploy: # Builds and Deploys whole project - mandatory: PROFILE
	make build VERSION=$(BUILD_TAG)
	make push-images VERSION=$(BUILD_TAG)
	make deploy VERSION=$(BUILD_TAG)

populate-deployment-variables:
	echo "export DB_SERVER=$$(make -s aws-rds-describe-instance-value DB_INSTANCE=$(DB_SERVER_NAME) KEY_DOT_PATH=Endpoint.Address)"
	echo "export DB_USER_NAME=$$(make -s secret-get-existing-value NAME=$(DB_USER_NAME_SECRET_NAME) KEY=$(DB_USER_NAME_SECRET_KEY))"
	echo "export SLACK_WEBHOOK_URL=$$(make -s secret-get-existing-value NAME=$(SLACK_WEBHOOK_SECRET_NAME) KEY=$(SLACK_WEBHOOK_SECRET_KEY))"

build-lambda: ### Build lambda docker image - mandatory: NAME
	UNDERSCORE_NAME=$$(echo $(NAME) | tr '-' '_')
	cp -f $(APPLICATION_DIR)/$$UNDERSCORE_NAME/requirements.txt $(DOCKER_DIR)/lambda/assets/requirements.txt
	cd $(APPLICATION_DIR)/$$UNDERSCORE_NAME
	tar -czf $(DOCKER_DIR)/lambda/assets/app.tar.gz \
		--exclude=tests *.py ../common/*.py > /dev/null 2>&1
	cd $(PROJECT_DIR)
	make docker-image GENERIC_IMAGE_NAME=lambda BUILD_ARGS="--build-arg python_entrypoint_file=$$UNDERSCORE_NAME"
	rm -f $(DOCKER_DIR)/lambda/assets/*.tar.gz $(DOCKER_DIR)/lambda/assets/*.txt

unit-test-local:
	pyenv local .venv
	pip install -r application/requirements-dev.txt -r application/event_processor/requirements.txt -r application/event_replay/requirements.txt -r application/event_sender/requirements.txt -r application/fifo_dlq_handler/requirements.txt
	cd application
	python -m pytest --junitxml=./testresults.xml --cov-report term-missing  --cov-report xml:coverage.xml --cov=. -vv

unit-test:
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	CMD="python -m pytest application --junitxml=./testresults.xml --cov-report term-missing  --cov-report xml:coverage.xml --cov=. -vv" \
	ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/authoriser:/tmp/.packages/authoriser \
		--volume $(APPLICATION_DIR)/common:/tmp/.packages/common \
		--volume $(APPLICATION_DIR)/comparison_reporting:/tmp/.packages/comparison_reporting \
		--volume $(APPLICATION_DIR)/dos_api_gateway:/tmp/.packages/dos_api_gateway \
		--volume $(APPLICATION_DIR)/event_processor:/tmp/.packages/event_processor \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		--volume $(APPLICATION_DIR)/fifo_dlq_handler:/tmp/.packages/fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/cr_fifo_dlq_handler:/tmp/.packages/cr_fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/event_replay:/tmp/.packages/event_replay \
		--volume $(APPLICATION_DIR)/test_db_checker_handler:/tmp/.packages/test_db_checker_handler \
		--volume $(APPLICATION_DIR)/orchestrator:/tmp/.packages/orchestrator \
		--volume $(APPLICATION_DIR)/slack_messenger:/tmp/.packages/slack_messenger \
		"

coverage-report: # Runs whole project coverage unit tests
	make -s python-code-coverage CMD="-m pytest application" DIR=/ \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/authoriser:/tmp/.packages/authoriser \
		--volume $(APPLICATION_DIR)/common:/tmp/.packages/common \
		--volume $(APPLICATION_DIR)/comparison_reporting:/tmp/.packages/comparison_reporting \
		--volume $(APPLICATION_DIR)/dos_api_gateway:/tmp/.packages/dos_api_gateway \
		--volume $(APPLICATION_DIR)/event_processor:/tmp/.packages/event_processor \
		--volume $(APPLICATION_DIR)/event_sender:/tmp/.packages/event_sender \
		--volume $(APPLICATION_DIR)/fifo_dlq_handler:/tmp/.packages/fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/cr_fifo_dlq_handler:/tmp/.packages/cr_fifo_dlq_handler \
		--volume $(APPLICATION_DIR)/event_replay:/tmp/.packages/event_replay \
		--volume $(APPLICATION_DIR)/test_db_checker_handler:/tmp/.packages/test_db_checker_handler \
		--volume $(APPLICATION_DIR)/orchestrator:/tmp/.packages/orchestrator \
		--volume $(APPLICATION_DIR)/slack_messenger:/tmp/.packages/slack_messenger \
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
	TEST_DB_CHECKER_FUNCTION_NAME=$(TF_VAR_test_db_checker_lambda_name) \
	EVENT_REPLAY=$(TF_VAR_event_replay_lambda_name) \
	DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
	DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
	KEYALIAS=${TF_VAR_signing_key_alias} \
	RUN_ID=${RUN_ID} \
	pytest steps -k $(TAGS) -vv --gherkin-terminal-reporter -p no:sugar -n 8 --cucumberjson=./testresults.json

integration-test-autoflags-no-logs: #End to end test DI project - mandatory: PROFILE; optional: ENVIRONMENT, PARALLEL_TEST_COUNT
	aws appconfig get-configuration --application uec-dos-int-test-lambda-app-config --environment test \
	--configuration event-processor --client-id test-id test_tmp.txt
	VALUE=$$(jq ".accepted_org_types.rules.org_type_in_list.conditions[0].value" test_tmp.txt)
	if [[ $$VALUE =~ .*"PHA".* ]]; then
		echo "PHA"
		NO_LOG_TAG="pharmacy_no_log_searches"
	elif [[ $$VALUE =~ .*"Dentist".* ]]; then
		echo "Dentist"
		NO_LOG_TAG="dentist_no_log_searches"
	fi
	rm -rf test_tmp.txt
	make integration-test TAGS=$$NO_LOG_TAG PROFILE=$(PROFILE) ENVIRONMENT=$(ENVIRONMENT) PARALLEL_TEST_COUNT=$(PARALLEL_TEST_COUNT)

integration-test-autoflags-cloudwatch-logs: #End to end test DI project - mandatory: PROFILE; optional: ENVIRONMENT, PARALLEL_TEST_COUNT
	aws appconfig get-configuration --application uec-dos-int-test-lambda-app-config --environment test \
	--configuration event-processor --client-id test-id test_tmp.txt
	VALUE=$$(jq ".accepted_org_types.rules.org_type_in_list.conditions[0].value" test_tmp.txt)
	if [[ $$VALUE =~ .*"PHA".* ]]; then
		echo "PHA"
		COULDWATCH_LOG_TAG="pharmacy_cloudwatch_queries"
	elif [[ $$VALUE =~ .*"Dentist".* ]]; then
		echo "Dentist"
		COULDWATCH_LOG_TAG="dentist_cloudwatch_queries"
	fi
	rm -rf test_tmp.txt
	make integration-test TAGS=$$COULDWATCH_LOG_TAG PROFILE=$(PROFILE) ENVIRONMENT=$(ENVIRONMENT) PARALLEL_TEST_COUNT=$(PARALLEL_TEST_COUNT)

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
		-e DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
		-e DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
		-e RUN_ID=${RUN_ID} \
		-e CR_FIFO_DLQ=$(TF_VAR_cr_fifo_dlq_handler_lambda_name) \
		"

create-dentist-reports: # Must use a PROFILE argument with appropriate DB details, or manually pass in details as arguments themselves
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	CMD="python application/comparison_reporting/run_dentist_reports.py" \
	ARGS=" \
		-e DB_SERVER=$$(make -s aws-rds-describe-instance-value DB_INSTANCE=$(DB_SERVER_NAME) KEY_DOT_PATH=Endpoint.Address) \
		-e DB_PORT=$(DB_PORT) \
		-e DB_NAME=$(DB_NAME) \
		-e DB_USER_NAME=$$(make -s secret-get-existing-value NAME=$(DB_USER_NAME_SECRET_NAME) KEY=$(DB_USER_NAME_SECRET_KEY)) \
		-e DB_SECRET_NAME=$(DB_SECRET_NAME) \
		-e DB_SECRET_KEY=$(DB_SECRET_KEY) \
		-e DB_SCHEMA=$(DB_SCHEMA) \
		--volume $(APPLICATION_DIR)/common:/tmp/.packages/common \
		--volume $(APPLICATION_DIR)/comparison_reporting:/tmp/.packages/comparison_reporting \
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
		slack-messenger-clean \
		orchestrator-clean \
		cr-fifo-dlq-handler-clean \
		event-replay-clean \
		test-db-checker-handler-clean \
		tester-clean \
		authoriser-clean \
		dos-api-gateway-clean \
		performance-test-clean

# ==============================================================================
# Event Sender

event-sender-build: ### Build event sender lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=event-sender

event-sender-build-and-deploy: ### Build and deploy event sender lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=event-sender

# ==============================================================================
# Slack Messenger

slack-messenger-build: ### Build slack messenger lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=slack-messenger

slack-messenger-build-and-deploy: ### Build and deploy slack messenger lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=slack-messenger

# ==============================================================================
# Event Processor

event-processor-build: ### Build event processor lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=event-processor

event-processor-build-and-deploy: ### Build and deploy event processor lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=event-processor

# ==============================================================================
# First In First Out Dead Letter Queue Handler (fifo-dlq-handler)

fifo-dlq-handler-build: ### Build fifo dlq handler lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=fifo-dlq-handler

fifo-dlq-handler-build-and-deploy: ### Build and deploy fifo dlq handler lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=fifo-dlq-handler

# ==============================================================================
# CR Fifo Dead Letter Queue Handler (cr-fifo-dlq-handler)

cr-fifo-dlq-handler-build: ### Build cr fifo dlq handler lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=cr-fifo-dlq-handler

cr-fifo-dlq-handler-build-and-deploy: ### Build and deploy cr fifo dlq handler lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=cr-fifo-dlq-handler

# ==============================================================================
# Event Replay lambda (event-replay)

event-replay-build: ### Build event replay lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=event-replay

event-replay-build-and-deploy: ### Build and deploy event replay lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=event-replay

# ==============================================================================
# Test DB Checker Handler (test-db-checker-handler)

test-db-checker-handler-build: ### Build test db checker handler lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=test-db-checker-handler

test-db-checker-handler-build-and-deploy: ### Build and deploy test db checker handler lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=test-db-checker-handler

# ==============================================================================
# Orchestrator

orchestrator-build: ### Build orchestrator lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=orchestrator

orchestrator-build-and-deploy: ### Build and deploy orchestrator lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=orchestrator

# ==============================================================================
# Authoriser (for dos api gateway mock)

authoriser-build: ### Build authoriser lambda docker image
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=authoriser

# ==============================================================================
# DoS API Gateway Mock lambda

dos-api-gateway-build:
	make build-lambda GENERIC_IMAGE_NAME=lambda NAME=dos-api-gateway

mock-dos-api-gateway-deployment:
	make terraform-apply-auto-approve STACKS=dos-api-gateway-mock

# ==============================================================================
# Deployments

sls-only-deploy: # Deploys all lambdas - mandatory: PROFILE, VERSION=[commit hash-timestamp/latest]
	eval "$$(make -s populate-deployment-variables)"
	make serverless-deploy

quick-build-and-deploy: # Build and deploy lambdas only (meant to for fast redeployment of existing lambdas) - mandatory: PROFILE, ENVIRONMENT
	make -s build VERSION=$(BUILD_TAG)
	make -s push-images VERSION=$(BUILD_TAG)
	make -s sls-only-deploy VERSION=$(BUILD_TAG)

build-and-deploy-single-function: # Build and deploy single lambda only (meant to for fast redeployment of existing lambda) - mandatory: PROFILE, ENVIRONMENT
	make $(FUNCTION_NAME)-build VERSION=$(BUILD_TAG)
	make docker-push NAME=$(FUNCTION_NAME) VERSION=$(BUILD_TAG)
	eval "$$(make -s populate-deployment-variables)"
	make serverless-deploy-single-function FUNCTION_NAME=$(FUNCTION_NAME) VERSION=$(BUILD_TAG)

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
	make docker-push NAME=slack-messenger

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
	if [ "$(PROFILE)" == "tools" ]; then
		TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-apply-auto-approve STACKS=deployment-pipelines TF_VAR_github_token=$$TF_VAR_github_token
	else
		echo "PROFILE must be tools and ENVIRONMENT must be dev"
	fi

undeploy-deployment-pipelines:
	if [ "$(PROFILE)" == "tools" ]; then
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

deploy-perf-test-tools:
	make terraform-apply-auto-approve STACKS=perf-test-tools PROFILE=tools

undeploy-perf-test-tools:
	make terraform-destroy-auto-approve STACKS=perf-test-tools PROFILE=tools

plan-perf-test-tools:
	if [ "$(PROFILE)" == "tools" ]; then
		export TF_VAR_github_token=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS) KEY=GITHUB_TOKEN)
		make terraform-plan STACKS=perf-test-tools
	else
		echo "Only tools profile supported at present"
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
		echo Recommended: you run this command from the main branch
	fi

tag-commit-to-destroy-environment: # Tag git commit to destroy deployment - mandatory: ENVIRONMENT=[di-number], COMMIT=[short commit hash]
	if [ "$(PROFILE)" != "$(ENVIRONMENT)" ]; then
		tag=$(ENVIRONMENT)-destroy-$(BUILD_TIMESTAMP)
		make git-tag-create TAG=$$tag COMMIT=$(COMMIT)
	else
		echo This is for destroying old task environments PROFILE should not be equal to ENVIRONMENT
	fi

get-environment-from-pr:
	ENVIRONMENT=$$(gh pr list -s merged --json number,mergeCommit,headRefName --repo=nhsd-exeter/dos-integration |  jq --raw-output '.[] | select(.number == $(PR_NUMBER)) | .headRefName | sub( ".*:*/DI-(?<x>.[0-9]*).*"; "di-\(.x)") ')
	echo $$ENVIRONMENT

is-environment-deployed:
	ENVIRONMENT_DEPLOYED=$$(aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --max-items 1000 | jq --raw-output '.StackSummaries[] | select(.StackName | contains("$(ENVIRONMENT)"))')
	echo $$ENVIRONMENT_DEPLOYED

slack-codebuild-notification: ### Send codebuild pipeline notification - mandatory: PIPELINE_NAME,BUILD_STATUS=[success|failure]
	time=$$(( $(shell date +"%s") - $(shell date -d '$(BUILD_DATE)' +"%s") ))
	make slack-send-notification \
		NAME=codebuild-pipeline-$(shell echo $(BUILD_STATUS) | tr '[:upper:]' '[:lower:]') \
		BUILD_TIME=$$(( $$time / 60 ))m$$(( $$time % 60 ))s \
		BUILD_URL=$$(echo https://$(AWS_REGION).console.aws.amazon.com/codesuite/codebuild/$(AWS_ACCOUNT_ID_MGMT)/projects/$(CODEBUILD_PROJECT_NAME)/build/$(CODEBUILD_BUILD_ID)/log?region=$(AWS_REGION)) \
		SLACK_WEBHOOK_URL=$$(make -s secret-get-existing-value NAME=$(SLACK_WEBHOOK_SECRET_NAME) KEY=$(SLACK_WEBHOOK_SECRET_KEY))

aws-ecr-cleanup: # Mandatory: REPOS=[comma separated list of ECR repo names e.g. event-sender,slack-messenger]
	export THIS_YEAR=$$(date +%Y)
	export LAST_YEAR=$$(date -d "1 year ago" +%Y)
	DELETE_IMAGES_OLDER_THAN=$$(date +%s --date='1 month ago')
	for REPOSITORY in $$(echo $(REPOS) | tr "," "\n"); do
		REPOSITORY_NAME=$$(echo $(PROJECT_GROUP_SHORT)/$(PROJECT_NAME_SHORT)/$$REPOSITORY)
		echo Repository is $$REPOSITORY_NAME
		make remove-untagged-images REPOSITORY=$$REPOSITORY_NAME
		make remove-task-images REPOSITORY=$$REPOSITORY_NAME DELETE_IMAGES_OLDER_THAN=$$DELETE_IMAGES_OLDER_THAN
	done

remove-task-images: # Removes task ecr images in repository older than certain date, REPOSITORY=[$(PROJECT_GROUP_SHORT)/$(PROJECT_NAME_SHORT)/REPOSITORY_NAME], DELETE_IMAGES_OLDER_THAN=[date/time in epoch]
	COUNTER=0
	IMAGE_IDS=$$(aws ecr describe-images --registry-id $(AWS_ACCOUNT_ID_MGMT) --region $(AWS_REGION) --repository-name $(REPOSITORY) --filter "tagStatus=TAGGED" --max-items 1000 --output json | jq -r '.imageDetails[] | select (.imageTags[0] | contains("$(LAST_YEAR)") or contains ("$(THIS_YEAR)")) | select (.imagePushedAt < $(DELETE_IMAGES_OLDER_THAN)).imageDigest')
	for DIGEST in $$(echo $$IMAGE_IDS | tr " " "\n"); do
			IMAGES_TO_DELETE+=$$(echo $$DIGEST | sed '$$s/$$/ /')
			COUNTER=$$((COUNTER+1))
			if [ $$COUNTER -eq 100 ]; then
				make batch-delete-ecr-images LIST_OF_DIGESTS="$$IMAGES_TO_DELETE"
				IMAGES_TO_DELETE=""
				COUNTER=0
			fi
	done
	if [[ ! -z "$$IMAGES_TO_DELETE" ]]; then
		make batch-delete-ecr-images LIST_OF_DIGESTS="$$IMAGES_TO_DELETE"
	fi

remove-untagged-images: # Removes untagged ecr images in repository, Mandatory - REPOSITORY=[$(PROJECT_GROUP_SHORT)/$(PROJECT_NAME_SHORT)/REPOSITORY_NAME]
	IMAGE_DIGESTS=$$(aws ecr describe-images --registry-id $(AWS_ACCOUNT_ID_MGMT) --region $(AWS_REGION) --region $(AWS_REGION) --repository-name $(REPOSITORY) --filter "tagStatus=UNTAGGED" --max-items 100 --output json | jq -r .imageDetails[].imageDigest | tr "\n" " ")
	if [[ ! -z "$$IMAGE_DIGESTS" ]]; then
		make batch-delete-ecr-images LIST_OF_DIGESTS="$$IMAGE_DIGESTS"
	fi

batch-delete-ecr-images: # Mandatory - LIST_OF_DIGESTS: [list of "sha:digest" separated by spaces], REPOSITORY=[$(PROJECT_GROUP_SHORT)/$(PROJECT_NAME_SHORT)/REPOSITORY_NAME]
	for DIGEST in $$(echo $(LIST_OF_DIGESTS) | tr " " "\n"); do
		IMAGES_TO_DELETE+=$$(echo imageDigest=\"$$DIGEST\" | sed 's/$$/ /')
	done
	IMAGE_IDS=$$(echo $$IMAGES_TO_DELETE | sed 's/ $$//')
	aws ecr batch-delete-image --registry-id $(AWS_ACCOUNT_ID_MGMT) --region $(AWS_REGION) --repository-name $(REPOSITORY) --image-ids $$IMAGE_IDS

# ==============================================================================
# Tester

tester-build: ### Build tester docker image
	cp -f $(APPLICATION_DIR)/requirements-dev.txt $(DOCKER_DIR)/tester/assets/
	cp -f $(APPLICATION_DIR)/event_processor/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-processor.txt
	cp -f $(APPLICATION_DIR)/event_sender/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-sender.txt
	cp -f $(APPLICATION_DIR)/slack_messenger/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-messenger.txt
	cp -f $(APPLICATION_DIR)/orchestrator/requirements.txt $(DOCKER_DIR)/tester/assets/requirements-orchestrator.txt
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

update-perf-environment-to-use-mock-api: # Updates the performance environment to connect to mock DoS API - mandatory: ENVIRONMENT=[perf|release number-perf e.g. 1-0-0-perf]
	IMAGE_TAG=$$(aws lambda get-function --function-name $(PROJECT_ID)-$(ENVIRONMENT)-event-processor | jq --raw-output ".Configuration.Environment.Variables.IMAGE_VERSION")
	eval "$$(make -s populate-deployment-variables PROFILE=perf)"
	make serverless-deploy PROFILE=perf VERSION=$$IMAGE_TAG

update-perf-environment-to-use-real-api: # Updates the performance environment to connect to real DoS API - mandatory: ENVIRONMENT=[perf|release number-perf e.g. 1-0-0-perf]
	IMAGE_TAG=$$(aws lambda get-function --function-name $(PROJECT_ID)-$(ENVIRONMENT)-event-processor | jq --raw-output ".Configuration.Environment.Variables.IMAGE_VERSION")
	eval "$$(make -s populate-deployment-variables PROFILE=perf-to-dos)"
	make serverless-deploy PROFILE=perf-to-dos VERSION=$$IMAGE_TAG

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

trigger-dos-deployment-pipeline:
	JENKINS_URL=$$(make -s secret-get-existing-value NAME=uec-dos-int-dev/deployment KEY=JENKINS_MOM_URL)
	JENKINS_USERNAME=$$(make -s secret-get-existing-value NAME=uec-dos-int-dev/deployment KEY=JENKINS_API_USERNAME)
	JENKINS_PASSWORD=$$(make -s secret-get-existing-value NAME=uec-dos-int-dev/deployment KEY=JENKINS_API_PASSWORD)
	JENKINS_CRUMB=$$(curl -L -X GET "$$JENKINS_URL/crumbIssuer/api/json" --user $$JENKINS_USERNAME:$$JENKINS_PASSWORD --cookie-jar jenkins.cookies | jq --raw-output '.crumb')
	curl -L -X POST "$$JENKINS_URL/view/DoS/job/dos-deploy/job/develop/buildWithParameters" --cookie jenkins.cookies \
	--user $$JENKINS_USERNAME:$$JENKINS_PASSWORD \
	-H "Jenkins-Crumb: $$JENKINS_CRUMB" \
	-F "TARGET=\"regressiondi\"" \
	-F "IMAGE_TAG=\"7.8.0_9525147\"" \
	-F "REFRESH=\"true\""
	echo Jenkins Job has started
	echo Sleeping for 5 minutes
	sleep 300
	echo Jenkins Job expected to have finished
	rm -rf jenkins.cookies

python-linting:
	make python-code-check FILES=application
	make python-code-check FILES=test

python-dead-code-scanning:
	make -s docker-run-python \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=$(APPLICATION_DIR) \
		CMD="python -m vulture"

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

terraform-security:
	make docker-run-terraform-tfsec DIR=infrastructure CMD="tfsec"

# ==============================================================================
# Checkov (Code Security Best Practices)

docker-best-practices:
	make docker-run-checkov DIR=/build/docker CHECKOV_OPTS="--framework dockerfile --skip-check CKV_DOCKER_2,CKV_DOCKER_3,CKV_DOCKER_4"

serverless-best-practices:
	make docker-run-checkov DIR=/deployment CHECKOV_OPTS="--framework serverless"

terraform-best-practices:
	make docker-run-checkov DIR=/infrastructure CHECKOV_OPTS="--framework terraform --skip-check CKV_AWS_7,CKV_AWS_115,CKV_AWS_116,CKV_AWS_117,CKV_AWS_120,CKV_AWS_147,CKV_AWS_149,CKV_AWS_158,CKV_AWS_173,CKV_AWS_219,CKV_AWS_225,CKV2_AWS_29"

github-actions-best-practices:
	make docker-run-checkov DIR=/.github CHECKOV_OPTS="--skip-check CKV_GHA_2"

checkov-secret-scanning:
	make docker-run-checkov CHECKOV_OPTS="--framework secrets"
