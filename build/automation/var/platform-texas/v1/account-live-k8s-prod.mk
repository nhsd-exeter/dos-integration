AWS_ACCOUNT_ID = $(AWS_ACCOUNT_ID_PROD)
AWS_ACCOUNT_NAME = prod

TEXAS_CERTIFICATE_ID = 8d65eee4-cf92-4a00-84de-7a9f544ba724
TEXAS_WAF_ACL_ID = ff530a4e-689d-4d90-b3ab-ac2160b5863d

TF_VAR_terraform_platform_state_store = nhsd-texasplatform-terraform-state-store-lk8s-$(AWS_ACCOUNT_NAME)

# ==============================================================================

include $(VAR_DIR)/platform-texas/platform-texas-v1.mk
