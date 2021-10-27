-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL := DEBUG
DOS_DEPLOYMENT_SECRETS := core-dos-dev/deployment
API_GATEWAY_USERNAME_KEY := DOS_API_GATEWAY_USER
API_GATEWAY_PASSWORD_KEY := DOS_API_GATEWAY_PASSWORD
CHANGE_REQUEST_ENDPOINT_TIMEOUT := 30
CHANGE_REQUEST_ENDPOINT_URL := //

# ==============================================================================
# Infrastructure variables (Terraform, Serverless, etc)

TF_VAR_api_gateway_api_key_name := $(PROJECT_ID)-$(ENVIRONMENT)-api-key
TF_VAR_nhs_uk_api_key_key := NHS_UK_API_KEY

TF_VAR_lambda_security_group_name := $(PROJECT_ID)-$(ENVIRONMENT)-lambda-sg
