-include $(VAR_DIR)/profile/prod.mk

# ==============================================================================
# Service variables

LOG_LEVEL:= INFO

DB_SERVER_NAME := uec-core-dos-uet-db-12
DB_REPLICA_SERVER_NAME := uec-core-dos-put-db-12-replica-di

DB_PORT := 5432
DB_NAME := pathwaysdos_ut
DB_SCHEMA := pathwaysdos
DB_SECRET_NAME := core-dos-uet-database-upgrade/deployment
DB_REPLICA_SECRET_NAME := core-dos-uet-database-upgrade/deployment
DB_REPLICA_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-demo/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

TF_VAR_ip_address_secret := uec-dos-int-demo-ip-addresses-allowlist
SLACK_WEBHOOK_SECRET_NAME = uec-dos-int-$(PROFILE)/deployment
SLACK_WEBHOOK_SECRET_KEY = SLACK_WEBHOOK
SLACK_ALERT_CHANNEL := dos-integration-dev-status

# ==============================================================================
# Organisation Types Feature Flags

ACCEPTED_ORG_TYPES := PHA
