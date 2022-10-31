PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

setup: project-config # Set up project
	make serverless-build
	make tester-build

build: # Build lambdas
	for IMAGE_NAME in $$(echo $(PROJECT_LAMBDAS_LIST) | tr "," "\n"); do
		make -s build-lambda GENERIC_IMAGE_NAME=lambda NAME=$$IMAGE_NAME
	done

build-lambda: ### Build lambda docker image - mandatory: NAME
	UNDERSCORE_LAMBDA_NAME=$$(echo $(NAME) | tr '-' '_')
	cp -f $(APPLICATION_DIR)/$$UNDERSCORE_LAMBDA_NAME/requirements.txt $(DOCKER_DIR)/lambda/assets/requirements.txt
	cd $(APPLICATION_DIR)
	tar -czf $(DOCKER_DIR)/lambda/assets/app.tar.gz \
		--exclude=tests $$UNDERSCORE_LAMBDA_NAME common/*.py __init__.py > /dev/null 2>&1
	cd $(PROJECT_DIR)
	make -s docker-image GENERIC_IMAGE_NAME=lambda CMD=$$UNDERSCORE_LAMBDA_NAME.$$UNDERSCORE_LAMBDA_NAME.lambda_handler
	rm -f $(DOCKER_DIR)/lambda/assets/*.tar.gz $(DOCKER_DIR)/lambda/assets/*.txt

build-and-push: # Build lambda docker images and pushes them to ECR
	for IMAGE_NAME in $$(echo $(PROJECT_LAMBDAS_LIST) | tr "," "\n"); do
		make -s build-lambda GENERIC_IMAGE_NAME=lambda NAME=$$IMAGE_NAME
		make -s docker-push NAME=$$IMAGE_NAME
	done

deploy: # Deploys whole project - mandatory: PROFILE
	eval "$$(make -s populate-deployment-variables)"
	make terraform-apply-auto-approve STACKS=api-key,appconfig,shared-resources,before-lambda-deployment
	eval "$$(make -s populate-serverless-variables)"
	make serverless-deploy
	make terraform-apply-auto-approve STACKS=after-lambda-deployment,blue-green-link

undeploy: # Undeploys whole project - mandatory: PROFILE
	eval "$$(make -s populate-deployment-variables)"
	make terraform-destroy-auto-approve STACKS=blue-green-link,after-lambda-deployment
	eval "$$(make -s populate-serverless-variables)"
	make serverless-remove VERSION="any"
	make terraform-destroy-auto-approve STACKS=before-lambda-deployment,shared-resources,appconfig
	if [ "$(PROFILE)" != "live" ]; then
		make terraform-destroy-auto-approve STACKS=api-key
	fi

build-and-deploy: # Builds and Deploys whole project - mandatory: PROFILE
	make build-and-push VERSION=$(BUILD_TAG)
	make deploy VERSION=$(BUILD_TAG)

populate-deployment-variables:
	echo "export DB_SERVER=$$(make -s aws-rds-describe-instance-value DB_INSTANCE=$(DB_SERVER_NAME) KEY_DOT_PATH=Endpoint.Address)"
	echo "export DB_REPLICA_SERVER=$$(make -s aws-rds-describe-instance-value DB_INSTANCE=$(DB_REPLICA_SERVER_NAME) KEY_DOT_PATH=Endpoint.Address)"
	DEPLOYMENT_SECRETS=$$(make -s secret-get-existing-value NAME=$(DEPLOYMENT_SECRETS))
	echo "export DB_READ_AND_WRITE_USER_NAME=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(DB_USER_NAME_SECRET_KEY)')"
	echo "export DB_READ_ONLY_USER_NAME=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(DB_READ_ONLY_USER_NAME_SECRET_KEY)')"
	echo "export SLACK_WEBHOOK_URL=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(SLACK_WEBHOOK_SECRET_KEY)')"
	echo "export PROJECT_SYSTEM_EMAIL_ADDRESS=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(SYSTEM_EMAIL_KEY)')"
	echo "export PROJECT_TEAM_EMAIL_ADDRESS=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(TEAM_EMAIL_KEY)')"
	echo "export PROJECT_SERVICE_CATEGORY=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(SERVICE_CATEGORY_KEY)')"
	echo "export PROJECT_DATA_CLASSIFICATION=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(DATA_CLASSIFICATION_KEY)')"
	echo "export PROJECT_DISTRIBUTION_LIST=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(DISTRIBUTION_LIST_KEY)')"
	echo "export TF_VAR_service_category=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(SERVICE_CATEGORY_KEY)')"
	echo "export TF_VAR_data_classification=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(DATA_CLASSIFICATION_KEY)')"
	echo "export TF_VAR_distribution_list=$$(echo $$DEPLOYMENT_SECRETS | jq -r '.$(DISTRIBUTION_LIST_KEY)')"

populate-serverless-variables:
	echo "export TERRAFORM_KMS_KEY_ID=$$(aws kms describe-key --key-id alias/$(TF_VAR_signing_key_alias) --query KeyMetadata.KeyId --output text)"

unit-test-local:
	pyenv local .venv
	pip install -r application/requirements-dev.txt -r application/service_matcher/requirements.txt -r application/event_replay/requirements.txt -r application/service_sync/requirements.txt -r application/change_event_dlq_handler/requirements.txt
	cd application
	python -m pytest --junitxml=./testresults.xml --cov-report term-missing  --cov-report xml:coverage.xml --cov=. -vv

unit-test:
	FOLDER_PATH=$$(make -s get-unit-test-path)
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	CMD="python -m pytest $$FOLDER_PATH --junitxml=./testresults.xml --cov-report term-missing  --cov-report xml:coverage.xml --cov=application -vv" \
	ARGS=$(UNIT_TEST_ARGS)

coverage-report: # Runs whole project coverage unit tests
	make -s python-code-coverage CMD="-m pytest application" DIR=/ \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	ARGS=$(UNIT_TEST_ARGS)

coverage-html:
	make -s docker-run-tools CMD="coverage html" DIR=/ \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		ARGS=$(UNIT_TEST_ARGS)

get-unit-test-path:
	if [ -z "$(LAMBDA_FOLDER_NAME)" ]; then
		echo application
	else
		echo application/$(LAMBDA_FOLDER_NAME)
	fi

UNIT_TEST_ARGS=" \
		-e POWERTOOLS_LOG_DEDUPLICATION_DISABLED="1" \
		--volume $(APPLICATION_DIR)/common:/tmp/.packages/common \
		--volume $(APPLICATION_DIR)/change_event_dlq_handler:/tmp/.packages/change_event_dlq_handler \
		--volume $(APPLICATION_DIR)/dos_db_update_dlq_handler:/tmp/.packages/dos_db_update_dlq_handler \
		--volume $(APPLICATION_DIR)/event_replay:/tmp/.packages/event_replay \
		--volume $(APPLICATION_DIR)/ingest_change_event:/tmp/.packages/ingest_change_event \
		--volume $(APPLICATION_DIR)/orchestrator:/tmp/.packages/orchestrator \
		--volume $(APPLICATION_DIR)/send_email:/tmp/.packages/send_email \
		--volume $(APPLICATION_DIR)/service_matcher:/tmp/.packages/service_matcher \
		--volume $(APPLICATION_DIR)/service_sync:/tmp/.packages/service_sync \
		--volume $(APPLICATION_DIR)/slack_messenger:/tmp/.packages/slack_messenger \
		"

integration-test-autoflags-no-logs: #End to end test DI project - mandatory: PROFILE; optional: ENVIRONMENT, PARALLEL_TEST_COUNT
	aws appconfig get-configuration --application uec-dos-int-$(ENVIRONMENT)-lambda-app-config --environment $(ENVIRONMENT) \
	--configuration ingest-change-event --client-id test-id test_tmp.txt
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
	aws appconfig get-configuration --application uec-dos-int-$(ENVIRONMENT)-lambda-app-config --environment $(ENVIRONMENT) \
	--configuration ingest-change-event --client-id test-id test_tmp.txt
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
	RUN_ID=$$RANDOM
	echo RUN_ID=$$RUN_ID
	make -s docker-run-tools \
	IMAGE=$$(make _docker-get-reg)/tester:latest \
	CMD="pytest steps -k $(TAGS) -vvvv --gherkin-terminal-reporter -p no:sugar -n $(PARALLEL_TEST_COUNT) --cucumberjson=./testresults.json" \
	DIR=./test/integration \
	ARGS=" \
		-e API_KEY_SECRET=$(TF_VAR_api_gateway_api_key_name) \
		-e NHS_UK_API_KEY=$(TF_VAR_nhs_uk_api_key_key) \
		-e DOS_DB_PASSWORD_SECRET_NAME=$(DB_SECRET_NAME) \
		-e DOS_DB_PASSWORD_KEY=$(DB_SECRET_KEY) \
		-e DOS_DB_USERNAME_SECRET_NAME=$(DB_USER_NAME_SECRET_NAME) \
		-e DOS_DB_USERNAME_KEY=$(DB_USER_NAME_SECRET_KEY) \
		-e URL=https://$(DOS_INTEGRATION_URL) \
		-e SERVICE_MATCHER=$(TF_VAR_service_matcher_lambda_name) \
		-e SERVICE_SYNC=$(TF_VAR_service_sync_lambda_name) \
		-e DOS_DB_HANDLER=$(TF_VAR_dos_db_handler_lambda_name) \
		-e EVENT_REPLAY=$(TF_VAR_event_replay_lambda_name) \
		-e DYNAMO_DB_TABLE=$(TF_VAR_change_events_table_name) \
		-e DOS_DB_IDENTIFIER_NAME=$(DB_SERVER_NAME) \
		-e RUN_ID=$$RUN_ID \
		-e CR_FIFO_DLQ=$(TF_VAR_dos_db_update_dlq_handler_lambda_name) \
		"

clean: # Runs whole project clean
	make \
		docker-clean \
		terraform-clean \
		serverless-clean \
		python-clean \
		tester-clean \
		performance-test-clean
	rm -rf test/integration/replay/.*.txt

# ==============================================================================
# Service Sync

service-sync-build-and-deploy: ### Build and deploy service sync lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=service-sync

# ==============================================================================
# Slack Messenger

slack-messenger-build-and-deploy: ### Build and deploy slack messenger lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=slack-messenger

# ==============================================================================
# Service Matcher

service-matcher-build-and-deploy: ### Build and deploy service matcher lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=service-matcher

# ==============================================================================
# Change Event Dead Letter Queue Handler (change-event-dlq-handler)

change-event-dlq-handler-build-and-deploy: ### Build and deploy change event dlq handler lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=change-event-dlq-handler

# ==============================================================================
# DoS DB Update Dead Letter Queue Handler (dos-db-update-dlq-handler) Nonprod only

dos-db-update-dlq-handler-build-and-deploy: ### Build and deploy dos db update dlq handler lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=dos-db-update-dlq-handler

# ==============================================================================
# Event Replay lambda (event-replay)

event-replay-build-and-deploy: ### Build and deploy event replay lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=event-replay

# ==============================================================================
# DoS DB Checker Handler (dos-db-handler)

dos-db-handler-build-and-deploy: ### Build and deploy test db checker handler lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=dos-db-handler

# ==============================================================================
# Orchestrator

orchestrator-build-and-deploy: ### Build and deploy orchestrator lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=orchestrator

# ==============================================================================
# Send Email

send-email-build-and-deploy: ### Build and deploy send email lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=send-email

# ==============================================================================
# Ingest Change Event

ingest-change-event-build-and-deploy: ### Build and deploy ingest change event lambda docker image - mandatory: PROFILE, ENVIRONMENT, FUNCTION_NAME
	make build-and-deploy-single-function FUNCTION_NAME=ingest-change-event

# ==============================================================================
# Deployments

sls-only-deploy: # Deploys all lambdas - mandatory: PROFILE, VERSION=[commit hash-timestamp/latest]
	eval "$$(make -s populate-deployment-variables)"
	eval "$$(make -s populate-serverless-variables)"
	make serverless-deploy

quick-build-and-deploy: # Build and deploy lambdas only (meant to for fast redeployment of existing lambdas) - mandatory: PROFILE, ENVIRONMENT
	make -s build VERSION=$(BUILD_TAG)
	make -s push-images VERSION=$(BUILD_TAG)
	make -s sls-only-deploy VERSION=$(BUILD_TAG)

build-and-deploy-single-function: # Build and deploy single lambda only (meant to for fast redeployment of existing lambda) - mandatory: PROFILE, ENVIRONMENT
	make build-lambda GENERIC_IMAGE_NAME=lambda VERSION=$(BUILD_TAG) NAME=$(FUNCTION_NAME)
	make docker-push NAME=$(FUNCTION_NAME) VERSION=$(BUILD_TAG)
	eval "$$(make -s populate-deployment-variables)"
	eval "$$(make -s populate-serverless-variables)"
	make serverless-deploy-single-function FUNCTION_NAME=$(FUNCTION_NAME) VERSION=$(BUILD_TAG)

push-images: # Use VERSION=[] to push a perticular version otherwise with default to latest
	for IMAGE_NAME in $$(echo $(PROJECT_LAMBDAS_LIST) | tr "," "\n"); do
		make docker-push NAME=$$IMAGE_NAME
	done

push-tester-image:
	make docker-push NAME=tester

# ==============================================================================
# SES (Simple Email Service)

deploy-email: # Deploys SES resources - mandatory: PROFILE=[live/test]
	make terraform-apply-auto-approve STACKS=email ENVIRONMENT=$(AWS_ACCOUNT_NAME)

undeploy-email: # Deploys SES resources - mandatory: PROFILE=[live/test]
	make terraform-destroy-auto-approve STACKS=email ENVIRONMENT=$(AWS_ACCOUNT_NAME)

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

deploy-perf-test-tools: # Deploys perf test tools terraform stack - mandatory: ENVIRONMENT. Shared Development ENVIRONMENT is tools
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

re-tag-images-for-deployment: # Re-tag ECR images for deployment - Mandatory: SOURCE=[tag], TARGET=[tag]
	for IMAGE_NAME in $$(echo $(PROJECT_LAMBDAS_PROD_LIST) | tr "," "\n"); do
		make docker-pull NAME=$$IMAGE_NAME VERSION=$(SOURCE)
		make docker-tag NAME=$$IMAGE_NAME SOURCE=$(SOURCE) TARGET=$(TARGET)
		make docker-push NAME=$$IMAGE_NAME VERSION=$(TARGET)
	done

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

aws-ecr-cleanup: # Mandatory: REPOS=[comma separated list of ECR repo names e.g. service-sync,slack-messenger]
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
	cat $(APPLICATION_DIR)/*/requirements.txt $(APPLICATION_DIR)/requirements-dev.txt | sort --unique > $(DOCKER_DIR)/tester/assets/requirements.txt
	make -s docker-image NAME=tester

tester-clean:
	rm -fv $(DOCKER_DIR)/tester/assets/*.txt

# ==============================================================================
# Testing

# -----------------------------
# Performance Testing

stress-test: # Create change events for stress performance testing - mandatory: PROFILE, ENVIRONMENT, START_TIME=[timestamp], optional: PIPELINE=true/false
	if [ $(PIPELINE) == true ]; then
		PERFORMANCE_ARGS=$$(echo --users 10 --spawn-rate 10 --run-time 1m)
	else
		PERFORMANCE_ARGS=$$(echo --users 10 --spawn-rate 2 --run-time 10m)
	fi
	make -s docker-run-tools \
		IMAGE=$$(make _docker-get-reg)/tester \
		CMD="python -m locust -f stress_test_locustfile.py --headless \
			$$PERFORMANCE_ARGS --stop-timeout 10 --exit-code-on-error 0 \
			-H https://$(DOS_INTEGRATION_URL) \
			--csv=results/$(START_TIME)_create_change_events" $(PERFORMANCE_TEST_DIR_AND_ARGS)

load-test: # Create change events for load performance testing - mandatory: PROFILE, ENVIRONMENT, START_TIME=[timestamp]
	make -s docker-run-tools \
		IMAGE=$$(make _docker-get-reg)/tester \
		CMD="python -m locust -f load_test_locustfile.py --headless \
			--users 50 --spawn-rate 2 --run-time 30m --stop-timeout 5	 --exit-code-on-error 0 \
			-H https://$(DOS_INTEGRATION_URL) \
			--csv=results/$(START_TIME)_create_change_events" $(PERFORMANCE_TEST_DIR_AND_ARGS)

PERFORMANCE_TEST_DIR_AND_ARGS= \
	DIR=./test/performance/create_change_events \
	ARGS="\
		-p 8089:8089 \
		-e API_KEY_SECRET_NAME=$(TF_VAR_api_gateway_api_key_name) \
		-e API_KEY_SECRET_KEY=$(TF_VAR_nhs_uk_api_key_key) \
		-e CHANGE_EVENTS_TABLE_NAME=$(TF_VAR_change_events_table_name) \
		"

performance-test-clean: # Clean up performance test results
	rm -rf $(TMP_DIR)/performance
	rm -f $(TMP_DIR)/*.zip
	rm -rf $(PROJECT_DIR)/test/performance/create_change_events/results/*.csv

stress-test-in-pipeline: # An all in one stress test make target
	START_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_START_TIME=$$(date +%FT%TZ)
	CODE_VERSION=$$($(AWSCLI) lambda get-function --function-name $(TF_VAR_service_matcher_lambda_name) | jq --raw-output '.Configuration.Environment.Variables.CODE_VERSION')
	make stress-test START_TIME=$$START_TIME PIPELINE=true
	sleep 4.5h
	END_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_END_TIME=$$(date +%FT%TZ)
	make send-performance-dashboard-slack-message START_DATE_TIME=$$AWS_START_TIME END_DATE_TIME=$$AWS_END_TIME

load-test-in-pipeline: # An all in one load test make target
	START_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_START_TIME=$$(date +%FT%TZ)
	CODE_VERSION=$$($(AWSCLI) lambda get-function --function-name $(TF_VAR_service_matcher_lambda_name) | jq --raw-output '.Configuration.Environment.Variables.CODE_VERSION')
	make load-test START_TIME=$$START_TIME
	sleep 10m
	END_TIME=$$(date +%Y-%m-%d_%H-%M-%S)
	AWS_END_TIME=$$(date +%FT%TZ)
	make send-performance-dashboard-slack-message START_DATE_TIME=$$AWS_START_TIME END_DATE_TIME=$$AWS_END_TIME

send-performance-dashboard-slack-message:
	make slack-codebuild-notification PROFILE=$(PROFILE) ENVIRONMENT=$(ENVIRONMENT) PIPELINE_NAME="$(PERF_TEST_TITLE) Tests Codebuild Stage" CODEBUILD_PROJECT_NAME=$(CB_PROJECT_NAME) CODEBUILD_BUILD_ID=$(CODEBUILD_BUILD_ID) SLACK_MESSAGE="Performance Dashboard Here - https://$(AWS_REGION).console.aws.amazon.com/cloudwatch/home?region=$(AWS_REGION)#dashboards:name=$(TF_VAR_cloudwatch_monitoring_dashboard_name);start=$(START_DATE_TIME);end=$(END_DATE_TIME)"

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
	-F "IMAGE_TAG=\"7.12.1_8659599\"" \
	-F "REFRESH=\"true\""
	echo Jenkins Job has started
	echo Sleeping for 3 minutes
	sleep 180
	echo Jenkins Job expected to have finished
	rm -rf jenkins.cookies

python-linting:
	make python-code-check FILES=application
	make python-code-check FILES=test

python-code-checks:
	make python-check-dead-code
	make python-check-imports
	make python-code-check FILES=application
	make python-code-check FILES=test
	make unit-test
	echo "Python code checks completed"

python-check-dead-code:
	make -s docker-run-python \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=$(APPLICATION_DIR) \
		CMD="python -m vulture"

python-format:
	make python-code-format FILES=application
	make python-code-format FILES=test

python-check-imports:
	make -s docker-run-python \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=$(APPLICATION_DIR) \
		CMD="python -m isort . -l=120 --check-only --profile=black \
			--force-alphabetical-sort-within-sections --known-local-folder=common \
			"

python-fix-imports:
	make -s docker-run-python \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=$(APPLICATION_DIR) \
		CMD="python -m isort . -l=120 --profile=black --force-alphabetical-sort-within-sections \
			--known-local-folder=common \
			"

python-check-security:
	make -s docker-run-python \
		IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=$(APPLICATION_DIR) \
		CMD="python -m bandit -r . -c pyproject.toml"

create-ecr-repositories:
	make docker-create-repository NAME=change-event-dlq-handler
	make docker-create-repository NAME=dos-db-handler
	make docker-create-repository NAME=dos-db-update-dlq-handler
	make docker-create-repository NAME=event-replay
	make docker-create-repository NAME=orchestrator
	make docker-create-repository NAME=service-matcher
	make docker-create-repository NAME=service-sync
	make docker-create-repository NAME=slack-messenger
	make docker-create-repository NAME=tester
	make docker-create-repository NAME=serverless

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

# ==============================================================================
# 6.0 Release targets

deploy-release-6-pipeline:
	make terraform-apply-auto-approve STACKS=release-6-0 PROFILE=tools ENVIRONMENT=dev

undeploy-release-6-pipeline:
	make terraform-destroy-auto-approve STACKS=release-6-0 PROFILE=tools ENVIRONMENT=dev

blue-green-move-terraform-resources:
# Init new shared resources state
	make _terraform-initialise STACK=shared-resources
# Import terraform resources
	make _terraform-stacks STACK=shared-resources CMD="import 'aws_dynamodb_table.message-history-table' $(TF_VAR_change_events_table_name)"
	SIGNING_KEY=$$(aws kms describe-key --key-id alias/$(TF_VAR_signing_key_alias) --query KeyMetadata.KeyId --output text)
	make _terraform-stacks STACK=shared-resources CMD="import 'aws_kms_key.signing_key' $$SIGNING_KEY"
	make _terraform-stacks STACK=shared-resources CMD="import 'aws_kms_alias.signing_key' alias/$(TF_VAR_signing_key_alias)"
	GLOBAL_REGION_SIGNING_KEY=$$(aws kms describe-key --region=$(TF_VAR_route53_health_check_alarm_region) --key-id alias/$(TF_VAR_route53_health_check_alarm_region_signing_key_alias) --query KeyMetadata.KeyId --output text)
	make _terraform-stacks STACK=shared-resources CMD="import 'aws_kms_key.route53_health_check_alarm_region_signing_key' $$GLOBAL_REGION_SIGNING_KEY"
	make _terraform-stacks STACK=shared-resources CMD="import 'aws_kms_alias.alarm_region_signing_key' alias/$(TF_VAR_route53_health_check_alarm_region_signing_key_alias)"
# Remove moved resources from current state
	make _terraform-stacks STACK=before-lambda-deployment CMD="state rm 'aws_dynamodb_table.message-history-table'"
	make _terraform-stacks STACK=before-lambda-deployment CMD="state rm 'aws_kms_key.signing_key'"
	make _terraform-stacks STACK=before-lambda-deployment CMD="state rm 'aws_kms_alias.signing_key'"
	make _terraform-stacks STACK=before-lambda-deployment CMD="state rm 'aws_kms_key.route53_health_check_alarm_region_signing_key'"
	make _terraform-stacks STACK=before-lambda-deployment CMD="state rm 'aws_kms_alias.alarm_region_signing_key'"
# Destroy non shared resources
	eval "$$(make -s populate-deployment-variables)"
	make terraform-destroy-auto-approve STACKS=after-lambda-deployment
	eval "$$(make -s populate-serverless-variables)"
	make serverless-remove VERSION="any"
	make terraform-destroy-auto-approve STACKS=before-lambda-deployment
	aws logs delete-log-group --log-group-name /aws/lambda/$(TF_VAR_orchestrator_lambda_name) 2> /dev/null ||:
# Rebuild resources
	eval "$$(make -s populate-deployment-variables)"
	make terraform-apply-auto-approve STACKS=shared-resources,before-lambda-deployment
	eval "$$(make -s populate-serverless-variables)"
	make serverless-deploy
	make terraform-apply-auto-approve STACKS=after-lambda-deployment,blue-green-link
