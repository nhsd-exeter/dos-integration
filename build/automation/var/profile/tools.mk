include $(VAR_DIR)/platform-texas/v2/account-tools.mk

# ==============================================================================
# Infrastructure variables

INFRASTRUCTURE_STACKS = terraform-state,networking,service-roles

# Terraform module configuration
TERRAFORM_STATE_KEY = $(TERRAFORM_STATE_KEY_SHARED)

# Terraform stacks configuration
TERRAFORM_STATE_BUCKET_NAME = $(TERRAFORM_STATE_STORE)
TERRAFORM_STATE_TABLE_NAME = $(TERRAFORM_STATE_LOCK)
TERRAFORM_NETWORKING_VPC_NAME = $(PROJECT_ID)-$(AWS_ACCOUNT_NAME)
TERRAFORM_NETWORKING_VPC_ID = 0
TERRAFORM_NETWORKING_ROUTE53_ZONE_NAME = $(PROJECT_GROUP_SHORT).$(TEXAS_TLD_NAME)
TERRAFORM_NHSD_IDENTITIES_ACCOUNT_ID = $(AWS_ACCOUNT_ID_IDENTITIES)
