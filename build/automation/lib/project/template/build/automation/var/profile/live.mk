include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# It is a Texas requirement that production namespaces end with `-prod`
K8S_APP_NAMESPACE := $(K8S_APP_NAMESPACE)-prod
K8S_JOB_NAMESPACE := $(K8S_JOB_NAMESPACE)-prod

# ==============================================================================
# Service variables

# ==============================================================================
# Infrastructure variables

DEPLOYMENT_STACKS = application
INFRASTRUCTURE_STACKS = database
