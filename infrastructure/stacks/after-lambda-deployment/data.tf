# ##############
# # LAMBDAS
# ##############

data "aws_lambda_function" "service_matcher" {
  function_name = var.service_matcher_lambda_name
}

data "aws_lambda_function" "ingest_change_event" {
  function_name = var.ingest_change_event_lambda_name
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

# ##############
# # KMS
# ##############

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}

# ##############
# # KINESIS
# ##############

data "aws_kinesis_firehose_delivery_stream" "dos_integration_firehose" {
  name = var.dos_integration_firehose
}

data "aws_kinesis_firehose_delivery_stream" "dos_firehose" {
  name = var.dos_firehose
}

# ##############
# # IAM
# ##############

data "aws_iam_role" "di_firehose_role" {
  name = var.di_firehose_role
}

data "aws_iam_role" "dos_firehose_role" {
  name = var.dos_firehose_role
}

# ##############
# # SNS
# ##############

data "aws_sns_topic" "sns_topic_app_alerts_for_slack_default_region" {
  name = var.sns_topic_app_alerts_for_slack_default_region
}

data "aws_sns_topic" "sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  provider = aws.route53_health_check_alarm_region
  name     = var.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region
}
