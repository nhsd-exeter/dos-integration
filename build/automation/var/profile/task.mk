-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

LOG_LEVEL := DEBUG

TF_VAR_api_gateway_api_key_name := $(PROJECT_ID)-$(ENVIRONMENT)-api-key
TF_VAR_nhs_uk_api_key_key := NHS_UK_API_KEY

TF_VAR_lambda_security_group_name := $(PROJECT_ID)-$(ENVIRONMENT)-lambda-sg
