-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL := DEBUG
DOS_API_GATEWAY_USERNAME := user
DOS_API_GATEWAY_PASSWORD := password
DOS_API_GATEWAY_REQUEST_TIMEOUT := 30
DOS_API_GATEWAY_URL := $(or $(DOS_API_GATEWAY_URL), "//")
MOCK_MODE := false

DB_SERVER_NAME := uec-core-dos-regression-db-9-replica-pu
DB_PORT := 5432
DB_NAME := postgres
DB_USER_NAME := dbuser
DB_SECRET_NAME := core-dos-dev/deployment
DB_SECRET_KEY := DB_SF_READONLY_PASSWORD
TF_VAR_dos_db_name := $(DB_SERVER_NAME)

# ==============================================================================
# Infrastructure variables (Terraform, Serverless, etc)
API_GATEWAY_API_KEY_NAME := $(PROJECT_ID)-$(ENVIRONMENT)-api-key
NHS_UK_API_KEY_KEY := NHS_UK_API_KEY

# API Gateway API Keys
TF_VAR_api_gateway_api_key_name := $(PROJECT_ID)-$(ENVIRONMENT)-api-key
TF_VAR_nhs_uk_api_key_key := NHS_UK_API_KEY

# Lambda Security Group
TF_VAR_lambda_security_group_name := $(PROJECT_ID)-$(ENVIRONMENT)-lambda-sg


# API Gateway Route53
TF_VAR_dos_integration_sub_domain_name := $(PROGRAMME)-$(TEAM_ID)-$(ENVIRONMENT)
DOS_INTEGRATION_URL := $(TF_VAR_dos_integration_sub_domain_name).$(TEXAS_HOSTED_ZONE)

# IAM Roles
TF_VAR_event_receiver_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-receiver-role
TF_VAR_event_processor_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor-role
TF_VAR_event_sender_role_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender-role

# Kinisis Firehose (Splunk Logs)
TF_VAR_dos_integration_firehose := $(PROJECT_ID)-cw-logs-firehose
TF_VAR_firehose_role := $(PROJECT_ID)_cw_firehose_access_role
TF_VAR_event_receiver_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-receiver-cw-logs-firehose-subscription
TF_VAR_event_processor_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor-cw-logs-firehose-subscription
TF_VAR_event_sender_subscription_filter_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender-cw-logs-firehose-subscription
TF_VAR_event_receiver_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-receiver
TF_VAR_event_processor_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-processor
TF_VAR_event_sender_lambda_name := $(PROJECT_ID)-$(ENVIRONMENT)-event-sender
