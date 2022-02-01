-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL:= DEBUG

DOS_API_GATEWAY_SECRETS = $(TF_VAR_dos_api_gateway_secret)
DOS_API_GATEWAY_USERNAME_KEY := DOS_API_GATEWAY_USERNAME
DOS_API_GATEWAY_PASSWORD_KEY := DOS_API_GATEWAY_PASSWORD
DOS_API_GATEWAY_REQUEST_TIMEOUT := 30
DOS_API_GATEWAY_URL := $(or $(DOS_API_GATEWAY_MOCK_URL), "//")
MOCK_MODE := false

DB_SERVER_NAME := uec-core-dos-regression-db-12-replica-di
DB_PORT := 5432
DB_NAME := pathwaysdos_regression
DB_SCHEMA := pathwaysdos
DB_SECRET_NAME := core-dos-dev/deployment
DB_SECRET_KEY := DB_SF_READONLY_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME
TF_VAR_dos_db_name := $(DB_SERVER_NAME)

# ==============================================================================
# Infrastructure variables (Terraform, Serverless, etc)

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
TF_VAR_dead_letter_queue_from_fifo_queue_name := $(PROJECT_ID)-$(ENVIRONMENT)-dead-letter-queue.fifo
SQS_QUEUE_URL:= https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT_ID)/$(TF_VAR_fifo_queue_name)
TF_VAR_ip_address_secret := uec-dos-int-task-ip-addresses-allowlist

# Dynamodb
TF_VAR_change_events_table_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-events

# Lambda IAM Roles
TF_VAR_event_processor_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor-role
TF_VAR_event_sender_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender-role
TF_VAR_fifo_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-dql-handler-role
TF_VAR_eventbridge_dlq_handler_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-eventbridge-dql-handler-role

# Kinisis Firehose (Splunk Logs)
TF_VAR_dos_integration_firehose := $(PROJECT_ID)-cw-logs-firehose
TF_VAR_firehose_role := $(PROJECT_ID)_cw_firehose_access_role
TF_VAR_event_processor_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor-cw-logs-firehose-subscription
TF_VAR_event_sender_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender-cw-logs-firehose-subscription
TF_VAR_change_event_gateway_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-event-api-gateway-cw-logs-firehose-subscription
TF_VAR_fifo_dlq_handler_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-dlq-handler-cw-logs-firehose-subscription
TF_VAR_eventbridge_dlq_handler_subscription_filter_name := $(PROFILE_ID)-$(ENVIRONMENT)-eventbridge-dlq-handler-cw-logs-firehose-subscription
TF_VAR_event_processor_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor
TF_VAR_event_sender_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender
TF_VAR_fifo_dlq_handler_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-fifo-dlq-handler
TF_VAR_eventbridge_dlq_handler_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-eventbridge-dlq-handler

# Mock DoS API Gateway Mock
TF_VAR_dos_api_gateway_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-mock
TF_VAR_dos_api_gateway_stage := $(ENVIRONMENT)
TF_VAR_dos_api_gateway_authoriser := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-mock-authoriser
TF_VAR_authoriser_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-authoriser
TF_VAR_image_version := $(or $(VERSION), latest)
TF_VAR_dos_api_gateway_secret := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-mock-secret
DOS_API_GATEWAY_MOCK_URL := https://$(TF_VAR_dos_api_gateway_name).$(TEXAS_HOSTED_ZONE)/change-request
TF_VAR_dos_api_gateway_secret_username_key := $(DOS_API_GATEWAY_USERNAME_KEY)
TF_VAR_dos_api_gateway_secret_password_key := $(DOS_API_GATEWAY_PASSWORD_KEY)
TF_VAR_dos_api_gateway_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-lambda
TF_VAR_powertools_service_name := $(PROGRAMME)-$(TEAM_ID)-$(ENVIRONMENT)


# Change Request Receiver API Key
TF_VAR_change_request_receiver_api_key_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-request-receiver-api-key
TF_VAR_change_request_receiver_api_key_key := CHANGE_REQUEST_RECEIVER_API_KEY

# Change Request Receiver Route53
CHANGE_REQUEST_RECEIVER_NAME := $(PROJECT_ID)-$(ENVIRONMENT)-change-request-receiver
TF_VAR_change_request_receiver_api_name := $(CHANGE_REQUEST_RECEIVER_NAME)
TF_VAR_change_request_receiver_subdomain_name := $(CHANGE_REQUEST_RECEIVER_NAME)

# Event Bridge
TF_VAR_eventbridge_bus_name := $(PROJECT_ID)-$(ENVIRONMENT)-eventbridge-bus
TF_VAR_change_request_eventbridge_rule_name := $(PROJECT_ID)-$(ENVIRONMENT)-change-request-rule
TF_VAR_dos_api_gateway_eventbridge_connection_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-connection
TF_VAR_dos_api_gateway_api_destination_name := $(PROJECT_ID)-$(ENVIRONMENT)-dos-api-gateway-api-destination
TF_VAR_dos_api_gateway_api_destination_url := https://$(TF_VAR_change_request_receiver_subdomain_name).$(TEXAS_HOSTED_ZONE)/change-request
TF_VAR_eventbridge_target_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-eventbridge-target-role
TF_VAR_eventbridge_target_policy_name	:= $(PROJECT_ID)-$(ENVIRONMENT)-eventbridge-target-policy
TF_VAR_dead_letter_queue_from_event_bus_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-bus-dead-letter-queue


TF_VAR_signing_key_alias := $(PROJECT_ID)-$(ENVIRONMENT)-signing-key-alias

# Cloudwatch performance dashboard
TF_VAR_cloudwatch_performance_dashboard_name := $(PROJECT_ID)-$(ENVIRONMENT)-performance
