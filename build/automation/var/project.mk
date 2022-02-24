ORG_NAME = nhsd-exeter
PROGRAMME = uec
PROJECT_GROUP = uec/dos
PROJECT_GROUP_SHORT = uec-dos
PROJECT_NAME = integration
PROJECT_NAME_SHORT = int
PROJECT_DISPLAY_NAME = DoS Integration
PROJECT_ID = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)
TEAM_NAME = DoS Integration
TEAM_ID = dos-integration

ROLE_PREFIX = UECCommon
PROJECT_TAG = $(PROJECT_NAME)
SERVICE_TAG = $(PROJECT_GROUP_SHORT)
SERVICE_TAG_COMMON = texas

PROJECT_TECH_STACK_LIST = python,terraform

DOCKER_REPOSITORIES =
SSL_DOMAINS_PROD =
DEPLOYMENT_SECRETS = $(PROJECT_ID)-$(PROFILE)/deployment

AWS_VPC_NAME = lk8s-$(AWS_ACCOUNT_NAME).texasplatform.uk
TF_VAR_aws_vpc_name = $(AWS_VPC_NAME)
SERVERLESS_PYTHON_VERSION_TAG = $(PYTHON_VERSION_MAJOR).$(PYTHON_VERSION_MINOR)
TF_VAR_team_id = $(TEAM_ID)
TF_VAR_programme = $(PROGRAMME)
TF_VAR_environment = $(ENVIRONMENT)
TF_VAR_github_owner = nhsd-exeter
TF_VAR_github_repo = dos-integration
PARALLEL_TEST_COUNT := $(or $(PARALLEL_TEST_COUNT) auto)

TF_VAR_dos_db_name := $(DB_SERVER_NAME)
ARTEFACTS := cr-fifo-dlq-handler,event-processor,event-replay,event-sender,fifo-dlq-handler,orchestrator
TF_VAR_docker_registry := $(DOCKER_REGISTRY)
DOS_API_GATEWAY_REQUEST_TIMEOUT := 30
# ==============================================================================
# Infrastructure variables (Terraform, Serverless, etc)
LOG_GROUP_NAME_PROCESSOR := /aws/lambda/$(PROJECT_ID)-$(ENVIRONMENT)-event-processor
LOG_GROUP_NAME_SENDER := /aws/lambda/$(PROJECT_ID)-$(ENVIRONMENT)-event-sender

# Change Event Receiver API Gateway API Keys
TF_VAR_api_gateway_api_key_name := $(PROJECT_ID)-$(ENVIRONMENT)-api-key
TF_VAR_nhs_uk_api_key_key := NHS_UK_API_KEY

# Lambda Security Group
TF_VAR_lambda_security_group_name := $(PROJECT_ID)-$(ENVIRONMENT)-lambda-sg

# Change Event Receiver API Gateway Route53 & SQS
TF_VAR_dos_integration_sub_domain_name := $(PROGRAMME)-$(TEAM_ID)-$(ENVIRONMENT)
DOS_INTEGRATION_URL := $(TF_VAR_dos_integration_sub_domain_name).$(TEXAS_HOSTED_ZONE)/v1/change-event
TF_VAR_di_endpoint_api_gateway_name := $(PROJECT_ID)-$(ENVIRONMENT)-di-endpoint
TF_VAR_di_endpoint_api_gateway_stage := $(ENVIRONMENT)
TF_VAR_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-queue.fifo

TF_VAR_cr_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-cr-fifo-queue.fifo

cr_fifo_queue_url := https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_cr_fifo_queue_name)
cr_dlq_queue_url := https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_cr_dead_letter_queue_from_fifo_queue_name)
TF_VAR_dead_letter_queue_from_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-dead-letter-queue.fifo
TF_VAR_cr_dead_letter_queue_from_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-cr-dead-letter-queue.fifo

# Dynamodb
TF_VAR_change_events_table_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-events

# Lambda IAM Roles
TF_VAR_event_processor_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor-role
TF_VAR_event_sender_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender-role
TF_VAR_fifo_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-dql-handler-role
TF_VAR_event_replay_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-replay-role
TF_VAR_cr_fifo_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-cr-fifo-dql-handler-role
TF_VAR_test_db_checker_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-test-db-checker-handler-role
TF_VAR_orchestrator_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-orchestrator-role

# Kinisis Firehose (Splunk Logs)
TF_VAR_dos_integration_firehose := $(PROJECT_ID)-cw-logs-firehose
TF_VAR_firehose_role := $(PROJECT_ID)_cw_firehose_access_role
TF_VAR_event_processor_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor-cw-logs-firehose-subscription
TF_VAR_event_sender_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender-cw-logs-firehose-subscription
TF_VAR_orchestrator_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-orchestrator-cw-logs-firehose-subscription
TF_VAR_change_event_gateway_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-api-gateway-cw-logs-firehose-subscription
TF_VAR_fifo_dlq_handler_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-dlq-handler-cw-logs-firehose-subscription
TF_VAR_cr_fifo_dlq_handler_subscription_filter_name := $(PROFILE_ID)-$(ENVIRONMENT)-cr-fifo-dlq-handler-cw-logs-firehose-subscription
TF_VAR_event_replay_subscription_filter_name := $(PROFILE_ID)-$(ENVIRONMENT)-eventbridge-dlq-handler-cw-logs-firehose-subscription
TF_VAR_event_processor_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor
TF_VAR_event_sender_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender
TF_VAR_fifo_dlq_handler_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-dlq-handler
TF_VAR_event_replay_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-replay
TF_VAR_test_db_checker_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-test-db-checker-handler
TF_VAR_cr_fifo_dlq_handler_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-cr-fifo-dlq-handler
TF_VAR_orchestrator_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-orchestrator
TF_VAR_change_request_gateway_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-request-api-gateway-cw-logs-firehose-subscription

# Mock DoS API Gateway Mock
TF_VAR_dos_api_gateway_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-mock
TF_VAR_dos_api_gateway_stage := $(ENVIRONMENT)
TF_VAR_dos_api_gateway_authoriser := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-mock-authoriser
TF_VAR_authoriser_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-authoriser
TF_VAR_image_version := $(or $(VERSION), latest)
TF_VAR_dos_api_gateway_secret := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-mock-secret
TF_VAR_dos_api_gateway_secret_username_key := $(DOS_API_GATEWAY_USERNAME_KEY)
TF_VAR_dos_api_gateway_secret_password_key := $(DOS_API_GATEWAY_PASSWORD_KEY)
TF_VAR_dos_api_gateway_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-lambda
TF_VAR_powertools_service_name := $(PROGRAMME)-$(TEAM_ID)-$(ENVIRONMENT)


TF_VAR_signing_key_alias := $(PROJECT_ID)-$(ENVIRONMENT)-signing-key-alias

# Cloudwatch monitoring dashboard
TF_VAR_cloudwatch_monitoring_dashboard_name := $(PROJECT_ID)-$(ENVIRONMENT)-monitoring-dashboard
TF_VAR_sqs_dlq_recieved_msg_alert_name := $(PROJECT_ID)-$(ENVIRONMENT)-sqs-dlq-recieved-msg-alert
TF_VAR_sns_topic_app_alerts_for_slack := $(PROJECT_ID)-$(ENVIRONMENT)-topic-app-alerts-for-slack

SQS_QUEUE_URL:= https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_fifo_queue_name)
DOS_TRANSACTIONS_PER_SECOND=3

# Performance Pipelines
TF_VAR_code_pipeline_branch_name := master
TF_VAR_pipeline_topic_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-topic
TF_VAR_pipeline_notification_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-notification
TF_VAR_pipeline_chatbot_channel := $(PROJECT_ID)-cicd-slk-channel
TF_VAR_nightly_rule_name := $(PROJECT_ID)-$(ENVIRONMENT)-performance-pipeline-nightly-rule
