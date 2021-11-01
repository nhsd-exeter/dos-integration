-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL := DEBUG
DOS_API_GATEWAY_USERNAME := user
DOS_API_GATEWAY_PASSWORD := password
DOS_API_GATEWAY_REQUEST_TIMEOUT := 30
DOS_API_GATEWAY_URL := $(or $(DOS_API_GATEWAY_URL), "//")

# ==============================================================================
# Infrastructure variables (Terraform, Serverless, etc)

API_GATEWAY_API_KEY_NAME := uec-dos-int-dev-api-key
NHS_UK_API_KEY_KEY := NHS_UK_API_KEY
