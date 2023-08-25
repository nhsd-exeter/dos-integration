-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL:= DEBUG

# DB Name
DB_CLUSTER_NAME := uec-core-dos-performance-cluster-14
DB_SERVER_NAME := uec-core-dos-performance-cluster-14-one
DB_REPLICA_SERVER_NAME := uec-core-dos-performance-cluster-14-two

# DB Route 53s
DB_ROUTE_53 := uec-core-dos-performance-primary.dos-db-sync-rds
DB_REPLICA_53 := uec-core-dos-performance-di-replica.dos-db-sync-rds

# DB Connection Variables
DB_PORT := 5432
DB_NAME := pathwaysdos
DB_SCHEMA := pathwaysdos

# DB Security Groups
DOS_DB_SG_NAME := uec-core-dos-performance-datastore-di-sg

# DB Secrets
DB_SECRET_NAME := uec-core-dos-performance-db-di-readwrite-user-password
DB_SECRET_KEY := DB_DI_READWRITE_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_USER_NAME_SECRET_KEY = DOS_DB_DI_USERNAME
DB_REPLICA_SECRET_NAME := uec-core-dos-performance-db-di-readonly-user-password
DB_REPLICA_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

# IP Address Secrets
TF_VAR_ip_address_secret := uec-dos-int-dev-ip-addresses-allowlist

# Slack Secrets
SLACK_WEBHOOK_SECRET_NAME = uec-dos-int-dev/deployment
SLACK_WEBHOOK_SECRET_KEY = SLACK_WEBHOOK
SLACK_ALERT_CHANNEL := dos-integration-dev-status

# Tag Secrets
TAG_SECRET_MANAGER := uec-dos-int-dev/deployment

# ==============================================================================
# Performance variables

SERVICE_MATCHER_MAX_CONCURRENCY := 28
SERVICE_SYNC_MAX_CONCURRENCY := 47

# ==============================================================================
# DoS DB Handler

DOS_DEPLOYMENT_SECRETS := null
DOS_DEPLOYMENT_SECRETS_PASSWORD_KEY := null
DOS_DB_HANDLER_DB_READ_AND_WRITE_USER_NAME := null
