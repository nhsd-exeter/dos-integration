resource "aws_cloudwatch_log_subscription_filter" "event_processor_logs_subscription_filter" {
  count           = var.profile == "task" ? 0 : 1
  name            = var.event_processor_subscription_filter_name
  role_arn        = data.aws_iam_role.firehose_role.arn
  log_group_name  = "/aws/lambda/${var.event_processor_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "event_sender_logs_subscription_filter" {
  count           = var.profile == "task" ? 0 : 1
  name            = var.event_sender_subscription_filter_name
  role_arn        = data.aws_iam_role.firehose_role.arn
  log_group_name  = "/aws/lambda/${var.event_sender_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "orchestrator_logs_subscription_filter" {
  count           = var.profile == "task" ? 0 : 1
  name            = var.orchestrator_subscription_filter_name
  role_arn        = data.aws_iam_role.firehose_role.arn
  log_group_name  = "/aws/lambda/${var.orchestrator_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "fifo_dlq_handler_logs_subscription_filter" {
  count           = var.profile == "task" ? 0 : 1
  name            = var.fifo_dlq_handler_subscription_filter_name
  role_arn        = data.aws_iam_role.firehose_role.arn
  log_group_name  = "/aws/lambda/${var.fifo_dlq_handler_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "cr_fifo_dlq_handler_logs_subscription_filter" {
  count           = var.profile == "task" ? 0 : 1
  name            = var.cr_fifo_dlq_handler_subscription_filter_name
  role_arn        = data.aws_iam_role.firehose_role.arn
  log_group_name  = "/aws/lambda/${var.cr_fifo_dlq_handler_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "event_replay_logs_subscription_filter" {
  count           = var.profile == "task" ? 0 : 1
  name            = var.event_replay_subscription_filter_name
  role_arn        = data.aws_iam_role.firehose_role.arn
  log_group_name  = "/aws/lambda/${var.event_replay_lambda_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}

resource "aws_cloudwatch_log_subscription_filter" "di_endpoint_access_logs" {
  count           = var.profile == "task" ? 0 : 1
  name            = var.change_event_gateway_subscription_filter_name
  role_arn        = data.aws_iam_role.firehose_role.arn
  log_group_name  = "/aws/api-gateway/${var.di_endpoint_api_gateway_name}"
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
}
