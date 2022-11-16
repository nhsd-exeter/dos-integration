include $(VAR_DIR)/platform-texas/v2/account-tools.mk

# ==============================================================================
# Infrastructure variables

INFRASTRUCTURE_STACKS = terraform-state,networking,service-roles

# Terraform module configuration
TERRAFORM_STATE_STORE = uec-dos-int-terraform-state
TERRAFORM_STATE_LOCK = uec-dos-int-terraform-state-lock

# Terraform stacks configuration
TERRAFORM_STATE_BUCKET_NAME = $(TERRAFORM_STATE_STORE)
TERRAFORM_STATE_TABLE_NAME = $(TERRAFORM_STATE_LOCK)
TERRAFORM_NETWORKING_VPC_NAME = $(PROJECT_ID)-$(AWS_ACCOUNT_NAME)
TERRAFORM_NETWORKING_VPC_ID = 0
TERRAFORM_NETWORKING_ROUTE53_ZONE_NAME = $(PROJECT_GROUP_SHORT).$(TEXAS_TLD_NAME)
TERRAFORM_NHSD_IDENTITIES_ACCOUNT_ID = $(AWS_ACCOUNT_ID_IDENTITIES)

TF_VAR_service_state_bucket = $(TERRAFORM_STATE_STORE)
TF_VAR_development_pipeline_state = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)/dev/development-pipeline/terraform.state
TF_VAR_mgmt_vpc_name := mgmt.texasplatform.uk
TF_VAR_developer_role_name = UECPUServiceDeveloper
