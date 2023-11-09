resource "aws_cloudwatch_log_subscription_filter" "change_event_dlq_handler_logs_subscription_filter" {
  name            = var.change_event_dlq_handler_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.change_event_dlq_handler_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "dos_db_update_dlq_handler_logs_subscription_filter" {
  name            = var.dos_db_update_dlq_handler_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.dos_db_handler_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "event_replay_logs_subscription_filter" {
  name            = var.event_replay_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.event_replay_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "ingest_change_event_logs_subscription_filter" {
  name            = var.ingest_change_event_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.ingest_change_event_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "send_email_logs_subscription_filter" {
  name            = var.send_email_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.send_email_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "service_matcher_logs_subscription_filter" {
  name            = var.service_matcher_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.service_matcher_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "service_sync_di_logs_subscription_filter" {
  name            = var.service_sync_di_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.service_sync_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "service_sync_dos_logs_subscription_filter" {
  count           = var.profile == "demo" ? 0 : 1
  name            = var.service_sync_dos_subscription_filter_name
  role_arn        = data.aws_iam_role.dos_firehose_role.arn
  log_group_name  = module.service_sync_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "elapsedTime=NULL"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "slack_messenger_logs_subscription_filter" {
  name            = var.slack_messenger_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.slack_messenger_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "quality_checker_logs_subscription_filter" {
  name            = var.quality_checker_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = module.quality_checker_lambda.lambda_cloudwatch_log_group_name
  filter_pattern  = "{ $.level = \"ERROR\" || $.level = \"WARNING\" || $.level = \"CRITICAL\" }"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}
