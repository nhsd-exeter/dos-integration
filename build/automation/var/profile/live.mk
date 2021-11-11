-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

LOG_LEVEL := INFO

# API Gateway Route53
TF_VAR_dos_integration_sub_domain_name := $(PROJECT_ID)-$(ENVIRONMENT)
