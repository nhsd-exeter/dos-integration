# ############################
# # SECRETS
# ############################

variable "api_gateway_api_key_name" {
  type        = string
  description = "Secret name for API Gateway API Key"
}

variable "nhs_uk_api_key_key" {
  type        = string
  description = "API Key secrets manager key"
}
