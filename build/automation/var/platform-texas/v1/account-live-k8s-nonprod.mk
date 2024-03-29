AWS_ACCOUNT_ID = $(AWS_ACCOUNT_ID_NONPROD)
AWS_ACCOUNT_NAME = nonprod

TEXAS_CERTIFICATE_ID = c0718115-4e22-4f48-a4aa-8c16ea86c5e6
TEXAS_WAF_ACL_ID = dfae6ec3-aa05-428f-a022-5fd85f646009

TF_VAR_terraform_platform_state_store = nhsd-texasplatform-terraform-state-store-live-lk8s-$(AWS_ACCOUNT_NAME)

TF_VAR_developer_role = UECDoSINTServiceDeveloper


SYSTEM_EMAIL_KEY := DI_SYSTEM_MAILBOX_ADDRESS
TEAM_EMAIL_KEY := DI_TEAM_MAILBOX_ADDRESS

TF_VAR_texas_hosted_zone = $(TEXAS_HOSTED_ZONE)
TF_VAR_ip_address_secret := uec-dos-int-dev-ip-addresses-allowlist
DEPLOYMENT_SECRETS = $(PROJECT_ID)-dev/deployment

# ==============================================================================

include $(VAR_DIR)/platform-texas/platform-texas-v1.mk
