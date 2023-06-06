resource "aws_cloudwatch_log_subscription_filter" "service_matcher_logs_subscription_filter" {
  name            = var.service_matcher_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.service_matcher_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}

resource "aws_cloudwatch_log_subscription_filter" "service_sync_di_logs_subscription_filter" {
  name            = var.service_sync_di_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.service_sync_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute, aws_cloudwatch_log_subscription_filter.service_sync_dos_logs_subscription_filter]
}

resource "aws_cloudwatch_log_subscription_filter" "service_sync_dos_logs_subscription_filter" {
  count           = var.profile == "demo" ? 0 : 1
  name            = var.service_sync_dos_subscription_filter_name
  role_arn        = data.aws_iam_role.dos_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.service_sync_lambda_name}"
  filter_pattern  = "elapsedTime=NULL"
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}

resource "aws_cloudwatch_log_subscription_filter" "change_event_dlq_handler_logs_subscription_filter" {
  name            = var.change_event_dlq_handler_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.change_event_dlq_handler_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}

resource "aws_cloudwatch_log_subscription_filter" "dos_db_update_dlq_handler_logs_subscription_filter" {
  name            = var.dos_db_update_dlq_handler_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}

resource "aws_cloudwatch_log_subscription_filter" "event_replay_logs_subscription_filter" {
  name            = var.event_replay_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.event_replay_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}
resource "aws_cloudwatch_log_subscription_filter" "slack_messenger_logs_subscription_filter" {
  name            = var.slack_messenger_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.slack_messenger_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}
resource "aws_cloudwatch_log_subscription_filter" "send_email_logs_subscription_filter" {
  name            = var.send_email_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.send_email_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}

resource "aws_cloudwatch_log_subscription_filter" "ingest_change_event_logs_subscription_filter" {
  name            = var.ingest_change_event_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = "/aws/lambda/${var.ingest_change_event_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [time_sleep.wait_a_minute]
}

resource "time_sleep" "wait_a_minute" {
  create_duration = "1m"
}
