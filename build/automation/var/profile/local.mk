-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk # To allow for docker build to work correct

# ==============================================================================
# Service Variables

API_GATEWAY_USERNAME := user
API_GATEWAY_PASSWORD := password
CHANGE_REQUEST_ENDPOINT_URL := http://mockserver:1080/api/change-request
CHANGE_REQUEST_ENDPOINT_TIMEOUT := 30

DB_SERVER := docker.for.mac.localhost
DB_PORT := 5432
DB_SCHEMA := public
DB_NAME := postgres
DB_USER_NAME := postgres
DB_PASSWORD := postgres
DB_SCHEMA := public

# ==============================================================================
# Component Test Variables

MOCKSERVER_URL := http://mockserver:1080
EVENT_RECEIVER_FUNCTION_URL := http://docker.for.mac.localhost:9000/2015-03-31/functions/function/invocations
EVENT_PROCESSOR_FUNCTION_URL := http://docker.for.mac.localhost:9001/2015-03-31/functions/function/invocations
EVENT_SENDER_FUNCTION_URL := http://docker.for.mac.localhost:9002/2015-03-31/functions/function/invocations
