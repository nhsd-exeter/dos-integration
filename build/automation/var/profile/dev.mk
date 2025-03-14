-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

LOG_LEVEL := DEBUG

# DB Name
DB_CLUSTER_NAME := uec-core-dos-regression-cluster-14
DB_WRITER_NAME := uec-core-dos-regression-cluster-14-one
DB_READER_NAME := uec-core-dos-regression-cluster-14-two

# DB Route 53s
DB_WRITER_ROUTE_53 := uec-core-dos-regression-dos-primary-rw.dos-datastore-regression
DB_READER_ROUTE_53 := uec-core-dos-regression-di-ro.dos-datastore-regression

# DB Connection Variables
DB_PORT := 5432
DB_NAME := pathwaysdos_regressiondi
DB_SCHEMA := pathwaysdos

# DB Security Groups
DB_SG_NAME := uec-core-dos-regression-datastore-di-sg

# DB Secrets
DB_WRITER_SECRET_NAME := core-dos-dev/deployment
DB_WRITER_SECRET_KEY := DB_DI_READWRITE_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_READER_SECRET_NAME := core-dos-dev/deployment
DB_READER_SECRET_KEY := DB_DI_READONLY_PASSWORD
DB_READ_ONLY_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_READ_ONLY_USER_NAME_SECRET_KEY = DOS_DB_REPLICA_DI_USERNAME

# IP Address Secrets
TF_VAR_ip_address_secret := uec-dos-int-dev-ip-addresses-allowlist

# Slack Secrets
SLACK_ALERT_CHANNEL := dos-integration-dev-status

# WAF
WAF_ENABLED := false
DDB_DELETE_PROTECTION :=false

# ==============================================================================
# Performance variables

SERVICE_MATCHER_MAX_CONCURRENCY := 20
SERVICE_SYNC_MAX_CONCURRENCY := 20

# ==============================================================================
# DoS DB Handler

DOS_DEPLOYMENT_SECRETS := core-dos-dev/deployment
DOS_DEPLOYMENT_SECRETS_PASSWORD_KEY := DB_RELEASE_USER_PASSWORD
DOS_DB_HANDLER_DB_READ_AND_WRITE_USER_NAME := pathwaysdos

# ==============================================================================
# Quality Checker Variables

ODSCODE_STARTING_CHARACTER := A
