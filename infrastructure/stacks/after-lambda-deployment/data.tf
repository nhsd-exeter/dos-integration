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

data "aws_lambda_function" "service_matcher" {
  function_name = var.service_matcher_lambda_name
}

data "aws_lambda_function" "change_event_dlq_handler" {
  function_name = var.change_event_dlq_handler_lambda_name
}

data "aws_lambda_function" "dos_db_update_dlq_handler" {
  function_name = var.dos_db_update_dlq_handler_lambda_name
}

data "aws_lambda_function" "send_email" {
  function_name = var.send_email_lambda_name
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

data "aws_kinesis_firehose_delivery_stream" "dos_firehose" {
  name = var.dos_firehose
}

data "aws_iam_role" "di_firehose_role" {
  name = var.di_firehose_role
}

data "aws_iam_role" "dos_firehose_role" {
  name = var.dos_firehose_role
}

data "aws_sns_topic" "sns_topic_app_alerts_for_slack" {
  name = var.sns_topic_app_alerts_for_slack
}
