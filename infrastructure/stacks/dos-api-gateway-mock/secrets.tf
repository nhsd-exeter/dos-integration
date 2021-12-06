resource "aws_secretsmanager_secret" "dos_api_gateway_secret" {
  name                    = var.dos_api_gateway_secret
  description             = "Connection details for DoS API Gateway ${var.environment}"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "dos_api_gateway_secret_version" {
  secret_id     = aws_secretsmanager_secret.dos_api_gateway_secret.id
  secret_string = "{\"${var.dos_api_gateway_secret_username_key}\" : \"${random_password.dos_api_gateway_username.result}-user\",\"${var.dos_api_gateway_secret_password_key}\" : \"${random_password.dos_api_gateway_password.result}\"}"
}

resource "random_password" "dos_api_gateway_username" {
  length      = 10
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  special     = false
}

resource "random_password" "dos_api_gateway_password" {
  length      = 30
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  special     = false
}
