#tfsec:ignore:aws-ssm-secret-use-customer-key
resource "aws_secretsmanager_secret" "api_gateway_api_key" {
  #checkov:skip=CKV2_AWS_57:Look to enable Secrets Manager secrets automatic rotation
  name                    = var.api_gateway_api_key_name
  description             = "API Key for DI AWS API Gateway"
  recovery_window_in_days = 0
}


resource "aws_secretsmanager_secret_version" "api_gateway_api_key" {
  #checkov:skip=CKV2_AWS_57:Look to enable Secrets Manager secrets automatic rotation
  secret_id     = aws_secretsmanager_secret.api_gateway_api_key.id
  secret_string = "{\"${var.nhs_uk_api_key_key}\" : \"${random_password.api_gateway_api_key.result}\"}"
}

resource "random_password" "api_gateway_api_key" {
  length      = 80
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  special     = false
}
