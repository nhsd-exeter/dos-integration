resource "aws_secretsmanager_secret" "api_gateway_api_key" {
  name                    = var.api_gateway_api_key
  description             = "API Key for DI AWS API Gateway"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "api_gateway_api_key" {
  secret_id     = aws_secretsmanager_secret.api_gateway_api_key.id
  secret_string = random_password.api_gateway_api_key.result
}

resource "random_password" "api_gateway_api_key" {
  length      = 25
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  special     = false
}
