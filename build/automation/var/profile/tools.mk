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


TF_VAR_code_pipeline_branch_name := master
TF_VAR_pipeline_topic_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-topic
TF_VAR_pipeline_notification_name := $(PROJECT_ID)-$(ENVIRONMENT)-pipeline-notification
TF_VAR_pipeline_chatbot_channel := $(PROJECT_ID)-cicd-slk-channel
TF_VAR_nightly_rule_name := $(PROJECT_ID)-$(ENVIRONMENT)-performance-pipeline-nightly-rule

TF_VAR_lambda_security_group_name := $(PROJECT_ID)-$(ENVIRONMENT)-lambda-sg
TF_VAR_test_signing_key_alias := $(PROJECT_ID)-test-signing-key-alias
TF_VAR_aws_np_vpc_name = lk8s-nonprod.texasplatform.uk

TF_VAR_service_state_bucket = $(TERRAFORM_STATE_STORE)
TF_VAR_development_pipeline_state = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)/dev/development-pipeline/terraform.state
