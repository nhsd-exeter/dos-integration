-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

TF_VAR_texas_hosted_zone = $(TEXAS_HOSTED_ZONE)
DOS_INTEGRATION_URL := $(TF_VAR_dos_integration_sub_domain_name).$(TEXAS_HOSTED_ZONE)/v1/change-event
