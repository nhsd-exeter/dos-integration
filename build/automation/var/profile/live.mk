-include $(VAR_DIR)/profile/prod.mk

# ==============================================================================
# Service variables

LOG_LEVEL:= INFO

DOS_API_GATEWAY_SECRETS = core-dos/deployment
DOS_API_GATEWAY_USERNAME_KEY := DOS_API_GATEWAY_USER
DOS_API_GATEWAY_PASSWORD_KEY := DOS_API_GATEWAY_PASSWORD
DOS_API_GATEWAY_URL := https://api-gateway.directoryofservices.nhs.uk/api/change-request

DB_SERVER_NAME := uec-core-dos-live-db-12-replica-di
DB_PORT := 5432
DB_NAME := pathwaysdos
DB_SCHEMA := pathwaysdos
DB_SECRET_NAME := core-dos/deployment
DB_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-live/deployment
DB_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

TF_VAR_ip_address_secret := uec-dos-int-live-ip-addresses-allowlist
SLACK_WEBHOOK_SECRET_NAME = uec-dos-int-live/deployment
SLACK_WEBHOOK_SECRET_KEY = SLACK_WEBHOOK
SLACK_ALERT_CHANNEL := dos-integration-live-status

# ==============================================================================
# Organisation Types Feature Flags

ACCEPTED_ORG_TYPES := PHA
