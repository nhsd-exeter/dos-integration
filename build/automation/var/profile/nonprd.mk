-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

TF_VAR_texas_hosted_zone = $(TEXAS_HOSTED_ZONE)
DOS_INTEGRATION_URL := $(TF_VAR_dos_integration_sub_domain_name).$(TEXAS_HOSTED_ZONE)/v1/change-event
DOS_API_GATEWAY_MOCK_URL := https://$(TF_VAR_dos_api_gateway_name).$(TEXAS_HOSTED_ZONE)/change-request
TF_VAR_ip_address_secret := uec-dos-int-dev-ip-addresses-allowlist

# ==============================================================================
# Organisation Types Feature Flags

ACCEPTED_ORG_TYPES := PHA,Dentist
