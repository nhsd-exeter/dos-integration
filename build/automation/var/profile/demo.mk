-include $(VAR_DIR)/profile/prod.mk

# ==============================================================================
# Service variables

LOG_LEVEL:= INFO

DOS_API_GATEWAY_SECRETS = core-dos-db-sync/deployment
DOS_API_GATEWAY_USERNAME_KEY := DOS_API_GATEWAY_USER
DOS_API_GATEWAY_PASSWORD_KEY := DOS_API_GATEWAY_PASSWORD
DOS_API_GATEWAY_REQUEST_TIMEOUT := 30
DOS_API_GATEWAY_URL := https://core-dos-performance-ddc-core-dos-api-gateway.k8s-nonprod.texasplatform.uk/api/change-request
MOCK_MODE := false

DB_SERVER_NAME := uec-core-dos-performance-db-12-replica-di
DB_PORT := 5432
DB_NAME := pathwaysdos
DB_SCHEMA := pathwaysdos
DB_SECRET_NAME := core-dos-dev/deployment
DB_SECRET_KEY := DB_SF_READONLY_PASSWORD
DB_USER_NAME_SECRET_NAME = uec-dos-int-dev/deployment
DB_USER_NAME_SECRET_KEY = DOS_REPLICA_DI_USERNAME

TF_VAR_ip_address_secret := uec-dos-int-dev-ip-addresses-allowlist
