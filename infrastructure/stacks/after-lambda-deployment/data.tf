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

data "aws_lambda_function" "cr_fifo_dlq_handler" {
  function_name = var.cr_fifo_dlq_handler_lambda_name
}

data "aws_secretsmanager_secret_version" "api_key" {
  secret_id = var.api_gateway_api_key_name
}

data "aws_secretsmanager_secret_version" "ip_address_secret" {
  secret_id = var.ip_address_secret
}

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}

data "aws_kinesis_firehose_delivery_stream" "dos_integration_firehose" {
  name = var.dos_integration_firehose
}

data "aws_iam_role" "firehose_role" {
  name = var.firehose_role
}
