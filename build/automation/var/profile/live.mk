-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# ==============================================================================
# Service variables

DEPLOYMENT_SECRETS = $(PROJECT_ID)-live/deployment # Move to project.mk when nonprod profiles are merged

LOG_LEVEL:= INFO

DB_SERVER_NAME := uec-core-dos-live-db-12
DB_ROUTE_53 := uec-core-dos-live-primary.dos-db-sync-rds
DB_REPLICA_SERVER_NAME := uec-core-dos-live-db-12-replica-di
DB_REPLICA_53 := uec-core-dos-live-db-replica-di.dos-db-sync-rds
DB_PORT := 5432
DB_NAME := pathwaysdos
DB_SCHEMA := pathwaysdos
DOS_DB_SG_NAME := live-lk8s-prod-core-dos-db-rds-postgres-sg
DOS_DB_REPLICA_SG_NAME := uec-core-dos-live-db-12-replica-di-sg

DB_SECRET_NAME := core-dos/deployment
DB_SECRET_KEY := DB_DI_READWRITE_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-live/deployment
DB_USER_NAME_SECRET_KEY = DOS_DB_DI_USERNAME

DB_REPLICA_SECRET_NAME := core-dos/deployment
DB_REPLICA_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-live/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

TF_VAR_ip_address_secret := uec-dos-int-live-ip-addresses-allowlist
SLACK_WEBHOOK_SECRET_NAME = uec-dos-int-live/deployment
SLACK_WEBHOOK_SECRET_KEY = SLACK_WEBHOOK
SLACK_ALERT_CHANNEL := dos-integration-live-status

TAG_SECRET_MANAGER := uec-dos-int-live/deployment

# ==============================================================================
# Organisation Types Feature Flags

ACCEPTED_ORG_TYPES := PHA
