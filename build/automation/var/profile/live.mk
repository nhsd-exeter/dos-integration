-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# ==============================================================================
# Service variables

DEPLOYMENT_SECRETS = $(PROJECT_ID)-live/deployment # Move to project.mk when nonprod profiles are merged

LOG_LEVEL:= INFO

# DB Name
DB_CLUSTER_NAME := uec-core-dos-live-cluster-14
DB_WRITER_NAME := uec-core-dos-live-cluster-14-one
DB_READER_NAME := uec-core-dos-live-cluster-14-two
# DB Route 53s
DB_WRITER_ROUTE_53 := uec-core-dos-live-primary.dos-db-sync-rds
DB_READER_ROUTE_53 := uec-core-dos-live-db-replica-di.dos-db-sync-rds

# DB Connection Variables
DB_PORT := 5432
DB_NAME := pathwaysdos
DB_SCHEMA := pathwaysdos

# DB Security Groups
DB_WRITER_SG_NAME := live-lk8s-prod-core-dos-db-rds-postgres-sg
DB_READER_SG_NAME := uec-core-dos-live-db-12-replica-di-sg

# DB Secrets
DB_WRITER_SECRET_NAME := core-dos/deployment
DB_WRITER_SECRET_KEY := DB_DI_READWRITE_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-live/deployment
DB_READER_SECRET_NAME := core-dos/deployment
DB_READER_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-live/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

# IP Address Secrets
TF_VAR_ip_address_secret := uec-dos-int-live-ip-addresses-allowlist

# Slack Secrets
SLACK_ALERT_CHANNEL := dos-integration-live-status

# WAF
WAF_ENABLED := true

# ==============================================================================
# Performance variables

SERVICE_MATCHER_MAX_CONCURRENCY := 28
SERVICE_SYNC_MAX_CONCURRENCY := 47

# ==============================================================================
# DoS DB Handler

DOS_DEPLOYMENT_SECRETS := null
DOS_DEPLOYMENT_SECRETS_PASSWORD_KEY := null
DOS_DB_HANDLER_DB_READ_AND_WRITE_USER_NAME := null
