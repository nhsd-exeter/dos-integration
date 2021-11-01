-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL := INFO
DOS_DEPLOYMENT_SECRETS := core-dos-dev/deployment
DOS_API_GATEWAY_USERNAME_KEY := DOS_API_GATEWAY_USER
DOS_API_GATEWAY_PASSWORD_KEY := DOS_API_GATEWAY_PASSWORD
DOS_API_GATEWAY_USERNAME := $(or $(DOS_API_GATEWAY_USERNAME), "")
DOS_API_GATEWAY_PASSWORD := $(or $(DOS_API_GATEWAY_PASSWORD), "")
DOS_API_GATEWAY_REQUEST_TIMEOUT := 30
DOS_API_GATEWAY_URL := $(or $(DOS_API_GATEWAY_URL), "//")

API_GATEWAY_API_KEY_NAME := uec-dos-int-$(PROFILE)-api-key
NHS_UK_API_KEY_KEY := NHS_UK_API_KEY
