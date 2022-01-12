data "terraform_remote_state" "route53" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.route53_terraform_state_key
    region = var.aws_region
  }
}
data "aws_acm_certificate" "issued" {
  domain   = "*.${var.texas_hosted_zone}"
  statuses = ["ISSUED"]
}

data "aws_lambda_function" "event_processor" {
  function_name = var.event_processor_lambda_name
}

data "aws_lambda_function" "fifo_dlq_handler" {
  function_name = var.fifo_dlq_handler_lambda_name
}

data "aws_secretsmanager_secret_version" "api_key" {
  secret_id = var.api_gateway_api_key_name
}
