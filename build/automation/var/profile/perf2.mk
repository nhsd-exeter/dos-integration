-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL := INFO

# DB Name
DB_CLUSTER_NAME := uec-core-dos-performance2-cluster-14
DB_WRITER_NAME := uec-core-dos-performance2-cluster-14-one
DB_READER_NAME := uec-core-dos-performance2-cluster-14-two

# DB Route 53s
DB_WRITER_ROUTE_53 := uec-core-dos-performance2-primary.dos-db-sync-rds
DB_READER_ROUTE_53 := uec-core-dos-performance2-di-replica.dos-db-sync-rds

# DB Connection Variables
DB_PORT := 5432
DB_NAME := pathwaysdos
DB_SCHEMA := pathwaysdos

# DB Security Groups
DB_WRITER_SG_NAME := uec-core-dos-performance2-datastore-sg
DB_READER_SG_NAME := uec-core-dos-performance2-db-12-replica-di-sg

# DB Secrets
DB_WRITER_SECRET_NAME := uec-core-dos-performance2-db-di-readwrite-user-password
DB_WRITER_SECRET_KEY := DB_DI_READWRITE_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_READER_SECRET_NAME := uec-core-dos-performance2-db-di-readonly-user-password
DB_READER_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

# IP Address Secrets
TF_VAR_ip_address_secret := uec-dos-int-dev-ip-addresses-allowlist

# Slack Secrets
SLACK_ALERT_CHANNEL := dos-integration-dev-status

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

# ==============================================================================
# Quality Checker Variables

ODSCODE_STARTING_CHARACTER := F
