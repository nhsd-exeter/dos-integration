-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# ==============================================================================
# Service variables
DEPLOYMENT_SECRETS = $(PROJECT_ID)-demo/deployment # Move to project.mk when nonprod profiles are merged

LOG_LEVEL := INFO

# DB Name
DB_CLUSTER_NAME := uec-core-dos-put-cluster-14
DB_WRITER_NAME := uec-core-dos-put-cluster-14-one
DB_READER_NAME := uec-core-dos-put-cluster-14-two

# DB Route 53s
DB_WRITER_ROUTE_53 := uec-core-dos-put-dos-primary-rw.dos-datastore-put
DB_READER_ROUTE_53 := uec-core-dos-put-di-ro.dos-datastore-put

# DB Connection Variables
DB_PORT := 5432
DB_NAME := pathwaysdos_uat3
DB_SCHEMA := pathwaysdos

# DB Security Groups
DB_SG_NAME := uec-core-dos-put-datastore-di-sg

# DB Secrets
DB_WRITER_SECRET_NAME := core-dos-uet-database-upgrade/deployment
DB_WRITER_SECRET_KEY := DB_DI_READWRITE_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-demo/deployment
DB_READER_SECRET_NAME := core-dos-uet-database-upgrade/deployment
DB_READER_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-demo/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

# IP Address Secrets
TF_VAR_ip_address_secret := uec-dos-int-demo-ip-addresses-allowlist

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

DOS_DEPLOYMENT_SECRETS := core-dos-uet/deployment
DOS_DEPLOYMENT_SECRETS_PASSWORD_KEY := DB_DI_READWRITE_PASSWORD
DOS_DB_HANDLER_DB_READ_AND_WRITE_USER_NAME = $(DB_READ_AND_WRITE_USER_NAME)

# ==============================================================================
# Quality Checker Variables

ODSCODE_STARTING_CHARACTER := F
