-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# ==============================================================================
# Service variables
DEPLOYMENT_SECRETS = $(PROJECT_ID)-demo/deployment # Move to project.mk when nonprod profiles are merged

LOG_LEVEL:= INFO

DB_SERVER_NAME := uec-core-dos-put-cluster-14-one
DB_ROUTE_53 := uec-core-dos-put-primary.dos-db-put
DB_REPLICA_SERVER_NAME := uec-core-dos-put-cluster-14-two
DB_REPLICA_53 := uec-core-dos-put-db-replica-di.dos-db-put
DB_PORT := 5432
DB_NAME := pathwaysdos_uat2
DB_SCHEMA := pathwaysdos
DOS_DB_SG_NAME := live-lk8s-prod-core-dos-db-put-rds-postgres-sg
DOS_DB_REPLICA_SG_NAME := uec-core-dos-put-db-12-replica-di-sg

DB_SECRET_NAME := core-dos-uet-database-upgrade/deployment
DB_SECRET_KEY := DB_DI_READWRITE_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-demo/deployment
DB_USER_NAME_SECRET_KEY = DOS_DB_DI_USERNAME

DB_REPLICA_SECRET_NAME := core-dos-uet-database-upgrade/deployment
DB_REPLICA_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-demo/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

TF_VAR_ip_address_secret := uec-dos-int-demo-ip-addresses-allowlist
SLACK_WEBHOOK_SECRET_NAME = uec-dos-int-demo/deployment
SLACK_WEBHOOK_SECRET_KEY = SLACK_WEBHOOK
SLACK_ALERT_CHANNEL := dos-integration-dev-status

TAG_SECRET_MANAGER := uec-dos-int-live/deployment

# ==============================================================================
# Organisation Types Feature Flags

ACCEPTED_ORG_TYPES := PHA

# ==============================================================================
# Performance variables

SERVICE_MATCHER_MAX_CONCURRENCY := 28
SERVICE_SYNC_MAX_CONCURRENCY := 47

# ==============================================================================
# DoS DB Handler

DOS_DEPLOYMENT_SECRETS := core-dos-uet/deployment
DOS_DEPLOYMENT_SECRETS_PASSWORD_KEY := DB_DI_READWRITE_PASSWORD
DOS_DB_HANDLER_DB_READ_AND_WRITE_USER_NAME = $(DB_READ_AND_WRITE_USER_NAME)
