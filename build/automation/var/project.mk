ORG_NAME = nhsd-exeter
PROGRAMME = uec
PROJECT_GROUP = uec/dos
PROJECT_GROUP_SHORT = uec-dos
PROJECT_NAME = integration
PROJECT_NAME_SHORT = int
PROJECT_DISPLAY_NAME = DoS Integration
PROJECT_ID = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)
TEAM_ID = dos-integration

ROLE_PREFIX = UECDoSInt
PROJECT_TAG = $(PROJECT_NAME)
SERVICE_TAG = $(PROJECT_GROUP_SHORT)
SERVICE_TAG_COMMON = texas

PROJECT_TECH_STACK_LIST = python,terraform
PROJECT_LAMBDAS_LIST = change-event-dlq-handler,dos-db-update-dlq-handler,event-replay,orchestrator,send-email,service-matcher,service-sync,slack-messenger,dos-db-handler,ingest-change-event
PROJECT_LAMBDAS_PROD_LIST = change-event-dlq-handler,dos-db-update-dlq-handler,event-replay,orchestrator,send-email,service-matcher,service-sync,slack-messenger,ingest-change-event
PROJECT_DEPLOYMENT_SECRETS = $(DEPLOYMENT_SECRETS)

AWS_VPC_NAME = lk8s-$(AWS_ACCOUNT_NAME).texasplatform.uk
TF_VAR_aws_vpc_name = $(AWS_VPC_NAME)
SLS_AWS_MONITORING_FREQUENCY = 500
TF_VAR_service_name=$(PROJECT_ID)
TF_VAR_team_id = $(TEAM_ID)
TF_VAR_programme = $(PROGRAMME)
TF_VAR_environment = $(ENVIRONMENT)
TF_VAR_aws_account_name = $(AWS_ACCOUNT_NAME)
TF_VAR_deployment_secrets = $(DEPLOYMENT_SECRETS)
TF_VAR_github_owner = nhsd-exeter
TF_VAR_github_repo = dos-integration
PARALLEL_TEST_COUNT := $(or $(PARALLEL_TEST_COUNT), auto)

TF_VAR_dos_db_name := $(DB_SERVER_NAME)
TF_VAR_dos_db_replica_name := $(DB_REPLICA_SERVER_NAME)

UNACCEPTABLE_VULNERABILITY_LEVELS = CRITICAL,HIGH,MEDIUM
DOS_TRANSACTIONS_PER_SECOND = 6

BLUE_GREEN_ENVIRONMENT := $(or $(BLUE_GREEN_ENVIRONMENT), $(ENVIRONMENT))
SHARED_ENVIRONMENT := $(or $(SHARED_ENVIRONMENT), $(ENVIRONMENT))
TF_VAR_blue_green_environment = $(BLUE_GREEN_ENVIRONMENT)
TF_VAR_shared_environment = $(SHARED_ENVIRONMENT)


# Performance Pipelines
TF_VAR_pipeline_topic_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-topic
TF_VAR_pipeline_notification_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-notification
TF_VAR_pipeline_chatbot_channel := $(PROJECT_ID)-cicd-slk-channel
TF_VAR_nightly_rule_name := $(PROJECT_ID)-$(ENVIRONMENT)-performance-pipeline-nightly-rule

# AppConfig
TF_VAR_accepted_org_types = $(ACCEPTED_ORG_TYPES)

# Development and Deployment Tools
TF_VAR_cicd_blue_green_deployment_pipeline_artefact_bucket := $(PROJECT_ID)-$(ENVIRONMENT)-cicd-blue-green-deployment-artefact-bucket
TF_VAR_development_pipeline_branch_name := develop
TF_VAR_cicd_blue_green_deployment_pipeline_name := $(PROJECT_ID)-$(ENVIRONMENT)-cicd-blue-green-deployment-pipeline
TF_VAR_blue_green_deployment_new_version_parameter_name := $(PROJECT_ID)-$(ENVIRONMENT)-blue-green-deployment-new-version

# ==============================================================================
# Infrastructure variables (Terraform, Serverless, etc)
# -------------------------------
# Common variables for all environments

# Tags
TF_VAR_tags_secret_manager = $(TAG_SECRET_MANAGER)
SERVICE_CATEGORY_KEY := DI_SERVICE_CATEGORY
DATA_CLASSIFICATION_KEY := DI_DATA_CLASSIFICATION
DISTRIBUTION_LIST_KEY := DI_DISTRIBUTION_LIST

# Global region
TF_VAR_route53_health_check_alarm_region = us-east-1

# Kinisis Firehose (Splunk Logs)
TF_VAR_dos_integration_firehose := $(PROJECT_ID)-cw-logs-firehose
TF_VAR_di_firehose_role := $(PROJECT_ID)_cw_firehose_access_role
TF_VAR_dos_firehose := dos-cw-logs-firehose
TF_VAR_dos_firehose_role := dos_cw_firehose_access_role

# -------------------------------
# SHARED ENVIRONMENT VARIABLES

# DI Endpoint API Gateway API Keys
TF_VAR_api_gateway_api_key_name := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-api-key
TF_VAR_nhs_uk_api_key_key := NHS_UK_API_KEY

# DI Endpoint API Gateway Route53 & SQS
TF_VAR_dos_integration_sub_domain_name := $(PROGRAMME)-$(TEAM_ID)-$(SHARED_ENVIRONMENT)
DOS_INTEGRATION_URL := $(TF_VAR_dos_integration_sub_domain_name).$(TEXAS_HOSTED_ZONE)/v1/change-event
TF_VAR_di_endpoint_api_gateway_name := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-di-endpoint
TF_VAR_di_endpoint_api_gateway_stage := $(SHARED_ENVIRONMENT)

# SQS Queues
TF_VAR_change_event_queue_name := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-change-event-queue.fifo
TF_VAR_change_event_dlq := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-change-event-dead-letter-queue.fifo

# Dynamodb
TF_VAR_change_events_table_name := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-change-events

# Log Group Filters for Firehose
TF_VAR_change_event_gateway_subscription_filter_name := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-change-event-api-gateway-cw-logs-firehose-subscription

# KMS
TF_VAR_signing_key_alias := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-signing-key-alias
TF_VAR_route53_health_check_alarm_region_signing_key_alias := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-alarm-region-signing-key-alias

# S3
SEND_EMAIL_BUCKET_NAME:=$(PROJECT_ID)-$(SHARED_ENVIRONMENT)-send-email-bucket
TF_VAR_send_email_bucket_name := $(SEND_EMAIL_BUCKET_NAME)

# Cloudwatch monitoring dashboard
TF_VAR_shared_resources_sns_topic_app_alerts_for_slack_default_region := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-shared-resources-topic-app-alerts-for-slack-default-region
TF_VAR_shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-shared-resources-topic-app-alerts-for-slack-route53-health-check-alarm-region

# Parameter Store
TF_VAR_blue_green_deployment_previous_version_parameter_name := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-blue-green-deployment-previous-version
TF_VAR_blue_green_deployment_current_version_parameter_name := $(PROJECT_ID)-$(SHARED_ENVIRONMENT)-blue-green-deployment-current-version

# -------------------------------
# BLUE/GREEN ENVIRONMENT VARIABLES

# Lambda Security Group
TF_VAR_lambda_security_group_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-lambda-sg

# SQS Queues
TF_VAR_holding_queue_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-holding-queue.fifo # TODO: Convert to standard queue when/if message grouping is implemented
TF_VAR_update_request_queue_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-update-request-queue.fifo
update_request_queue_url := https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_update_request_queue_name)
holding_queue_url := https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_holding_queue_name)
update_request_dlq_url := https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_update_request_dlq)
TF_VAR_holding_queue_dlq := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-holding-queue-dead-letter-queue.fifo
TF_VAR_update_request_dlq := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-update-request-dead-letter-queue.fifo

# Lambda IAM Roles
TF_VAR_change_event_dlq_handler_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-change-event-dlq-handler-role
TF_VAR_dos_db_handler_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-dos-db-handler-role
TF_VAR_dos_db_update_dlq_handler_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-dos-db-update-dlq-handler-role
TF_VAR_event_replay_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-event-replay-role
TF_VAR_ingest_change_event_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-ingest-change-event-role
TF_VAR_orchestrator_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-orchestrator-role
TF_VAR_send_email_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-send-email-role
TF_VAR_service_matcher_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-service-matcher-role
TF_VAR_service_sync_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-service-sync-role
TF_VAR_slack_messenger_role_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-slack-messenger-role

# Log Group Filters for Firehose
TF_VAR_change_event_dlq_handler_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-change-event-dlq-handler-cw-logs-firehose-subscription
TF_VAR_dos_db_update_dlq_handler_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-dos-db-update-dlq-handler-cw-logs-firehose-subscription
TF_VAR_event_replay_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-eventbridge-dlq-handler-cw-logs-firehose-subscription
TF_VAR_ingest_change_event_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-ingest-change-event-cw-logs-firehose-subscription
TF_VAR_orchestrator_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-orchestrator-cw-logs-firehose-subscription
TF_VAR_send_email_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-send-email-cw-logs-firehose-subscription
TF_VAR_service_matcher_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-service-matcher-cw-logs-firehose-subscription
TF_VAR_service_sync_di_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-service-sync-di-cw-logs-firehose-subscription
TF_VAR_service_sync_dos_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-service-sync-dos-cw-logs-firehose-subscription
TF_VAR_slack_messenger_subscription_filter_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-slack-messenger-cw-logs-firehose-subscription

# Lambda names
TF_VAR_change_event_dlq_handler_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-change-event-dlq-handler
TF_VAR_dos_db_handler_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-dos-db-handler
TF_VAR_dos_db_update_dlq_handler_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-dos-db-update-dlq-handler
TF_VAR_event_replay_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-event-replay
TF_VAR_ingest_change_event_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-ingest-change-event
TF_VAR_orchestrator_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-orchestrator
TF_VAR_send_email_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-send-email
TF_VAR_service_matcher_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-service-matcher
TF_VAR_service_sync_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-service-sync
TF_VAR_slack_messenger_lambda_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-slack-messenger

# Cloudwatch monitoring dashboard
TF_VAR_cloudwatch_monitoring_dashboard_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-monitoring-dashboard
TF_VAR_sqs_dlq_recieved_msg_alert_name := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-sqs-dlq-recieved-msg-alert
TF_VAR_sns_topic_app_alerts_for_slack_default_region := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-topic-app-alerts-for-slack-default-region
TF_VAR_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region := $(PROJECT_ID)-$(BLUE_GREEN_ENVIRONMENT)-topic-app-alerts-for-slack-route53-health-check-alarm-region
SQS_QUEUE_URL:= https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_change_event_queue_name)
