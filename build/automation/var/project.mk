ORG_NAME = nhsd-exeter
PROGRAMME = uec
PROJECT_GROUP = uec/dos
PROJECT_GROUP_SHORT = uec-dos
PROJECT_NAME = integration
PROJECT_NAME_SHORT = int
PROJECT_DISPLAY_NAME = DoS Integration
PROJECT_ID = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)
TEAM_ID = dos-integration

ROLE_PREFIX = UECCommon
PROJECT_TAG = $(PROJECT_NAME)
SERVICE_TAG = $(PROJECT_GROUP_SHORT)
SERVICE_TAG_COMMON = texas

PROJECT_TECH_STACK_LIST = python,terraform
PROJECT_LAMBDAS_LIST = change-event-dlq-handler,dos-db-update-dlq-handler,event-replay,orchestrator,send-email,service-matcher,service-sync,slack-messenger,dos-db-handler
PROJECT_LAMBDAS_PROD_LIST = change-event-dlq-handler,dos-db-update-dlq-handler,event-replay,orchestrator,send-email,service-matcher,service-sync,slack-messenger
DEPLOYMENT_SECRETS = $(PROJECT_ID)-$(PROFILE)/deployment

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
# ==============================================================================
# Infrastructure variables (Terraform, Serverless, etc)

# DI Endpoint API Gateway API Keys
TF_VAR_api_gateway_api_key_name := $(PROJECT_ID)-$(ENVIRONMENT)-api-key
TF_VAR_nhs_uk_api_key_key := NHS_UK_API_KEY

# Lambda Security Group
TF_VAR_lambda_security_group_name := $(PROJECT_ID)-$(ENVIRONMENT)-lambda-sg

# DI Endpoint API Gateway Route53 & SQS
TF_VAR_dos_integration_sub_domain_name := $(PROGRAMME)-$(TEAM_ID)-$(ENVIRONMENT)
DOS_INTEGRATION_URL := $(TF_VAR_dos_integration_sub_domain_name).$(TEXAS_HOSTED_ZONE)/v1/change-event
TF_VAR_di_endpoint_api_gateway_name := $(PROJECT_ID)-$(ENVIRONMENT)-di-endpoint
TF_VAR_di_endpoint_api_gateway_stage := $(ENVIRONMENT)

# SQS Queues
TF_VAR_change_event_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-queue.fifo
TF_VAR_update_request_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-update-request-queue.fifo
update_request_queue_url := https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_update_request_queue_name)
update_request_dlq_url := https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_update_request_dlq)
TF_VAR_change_event_dlq := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-dead-letter-queue.fifo
TF_VAR_update_request_dlq := $(PROJECT_ID)-$(ENVIRONMENT)-update-request-dead-letter-queue.fifo

# Dynamodb
TF_VAR_change_events_table_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-events

# Lambda IAM Roles
TF_VAR_change_event_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-dlq-handler-role
TF_VAR_dos_db_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-db-handler-role
TF_VAR_dos_db_update_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-db-update-dlq-handler-role
TF_VAR_event_replay_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-replay-role
TF_VAR_orchestrator_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-orchestrator-role
TF_VAR_send_email_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-send-email-role
TF_VAR_service_matcher_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-service-matcher-role
TF_VAR_service_sync_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-service-sync-role
TF_VAR_slack_messenger_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-slack-messenger-role
# Kinisis Firehose (Splunk Logs)
TF_VAR_dos_integration_firehose := $(PROJECT_ID)-cw-logs-firehose
TF_VAR_di_firehose_role := $(PROJECT_ID)_cw_firehose_access_role
TF_VAR_dos_firehose := dos-cw-logs-firehose
TF_VAR_dos_firehose_role := dos_cw_firehose_access_role

# Log Group Filters for Firehose
TF_VAR_change_event_dlq_handler_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-dlq-handler-cw-logs-firehose-subscription
TF_VAR_change_event_gateway_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-api-gateway-cw-logs-firehose-subscription
TF_VAR_dos_db_update_dlq_handler_subscription_filter_name := $(PROFILE_ID)-$(ENVIRONMENT)-dos-db-update-dlq-handler-cw-logs-firehose-subscription
TF_VAR_event_replay_subscription_filter_name := $(PROFILE_ID)-$(ENVIRONMENT)-eventbridge-dlq-handler-cw-logs-firehose-subscription
TF_VAR_orchestrator_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-orchestrator-cw-logs-firehose-subscription
TF_VAR_send_email_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-send-email-cw-logs-firehose-subscription
TF_VAR_service_matcher_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-service-matcher-cw-logs-firehose-subscription
TF_VAR_service_sync_di_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-service-sync-di-cw-logs-firehose-subscription
TF_VAR_service_sync_dos_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-service-sync-dos-cw-logs-firehose-subscription
TF_VAR_slack_messenger_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-slack-messenger-cw-logs-firehose-subscription
# Lambda names
TF_VAR_change_event_dlq_handler_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-dlq-handler
TF_VAR_dos_db_handler_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-db-handler
TF_VAR_dos_db_update_dlq_handler_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-db-update-dlq-handler
TF_VAR_event_replay_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-replay
TF_VAR_orchestrator_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-orchestrator
TF_VAR_send_email_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-send-email
TF_VAR_service_matcher_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-service-matcher
TF_VAR_service_sync_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-service-sync
TF_VAR_slack_messenger_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-slack-messenger

TF_VAR_powertools_service_name := $(PROGRAMME)-$(TEAM_ID)-$(ENVIRONMENT)
TF_VAR_signing_key_alias := $(PROJECT_ID)-$(ENVIRONMENT)-signing-key-alias
SEND_EMAIL_BUCKET_NAME:=$(PROJECT_ID)-$(ENVIRONMENT)-send-email-bucket
TF_VAR_send_email_bucket_name := $(SEND_EMAIL_BUCKET_NAME)
# Cloudwatch monitoring dashboard
TF_VAR_cloudwatch_monitoring_dashboard_name := $(PROJECT_ID)-$(ENVIRONMENT)-monitoring-dashboard
TF_VAR_sqs_dlq_recieved_msg_alert_name := $(PROJECT_ID)-$(ENVIRONMENT)-sqs-dlq-recieved-msg-alert
TF_VAR_sns_topic_app_alerts_for_slack := $(PROJECT_ID)-$(ENVIRONMENT)-topic-app-alerts-for-slack
SQS_QUEUE_URL:= https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_change_event_queue_name)

# Performance Pipelines
TF_VAR_pipeline_topic_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-topic
TF_VAR_pipeline_notification_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-notification
TF_VAR_pipeline_chatbot_channel := $(PROJECT_ID)-cicd-slk-channel
TF_VAR_nightly_rule_name := $(PROJECT_ID)-$(ENVIRONMENT)-performance-pipeline-nightly-rule

# AppConfig
TF_VAR_accepted_org_types = $(ACCEPTED_ORG_TYPES)

# ==============================================================================
# Old variables - TODO: Delete these after release 3.0
TF_VAR_event_processor_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor-role
TF_VAR_event_sender_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender-role
TF_VAR_fifo_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-dlq-handler-role
TF_VAR_cr_fifo_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-cr-fifo-dlq-handler-role
TF_VAR_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-queue.fifo
TF_VAR_cr_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-cr-fifo-queue.fifo
TF_VAR_dead_letter_queue_from_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-dead-letter-queue.fifo
TF_VAR_cr_dead_letter_queue_from_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-cr-dead-letter-queue.fifo
# ==============================================================================
