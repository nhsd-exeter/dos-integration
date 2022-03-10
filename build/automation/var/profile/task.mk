-include $(VAR_DIR)/profile/nonprd.mk

# ==============================================================================
# Service variables

LOG_LEVEL:= DEBUG

DOS_API_GATEWAY_SECRETS = $(TF_VAR_dos_api_gateway_secret)
DOS_API_GATEWAY_USERNAME_KEY := DOS_API_GATEWAY_USERNAME
DOS_API_GATEWAY_PASSWORD_KEY := DOS_API_GATEWAY_PASSWORD

DOS_API_GATEWAY_URL := $(or $(DOS_API_GATEWAY_MOCK_URL), "//")

DB_SERVER_NAME := uec-core-dos-regression-db-12-replica-di
DB_PORT := 5432
DB_NAME := pathwaysdos_regression
DB_SCHEMA := pathwaysdos
DB_SECRET_NAME := core-dos-dev/deployment
DB_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

TF_VAR_ip_address_secret := uec-dos-int-task-ip-addresses-allowlist
SLACK_WEBHOOK_SECRET_NAME = uec-dos-int-dev/deployment
SLACK_WEBHOOK_SECRET_KEY = SLACK_WEBHOOK
SLACK_ALERT_CHANNEL := dos-integration-dev-status
