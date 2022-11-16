resource "aws_cloudwatch_log_subscription_filter" "di_endpoint_access_logs" {
  name            = var.change_event_gateway_subscription_filter_name
  role_arn        = data.aws_iam_role.di_firehose_role.arn
  log_group_name  = aws_cloudwatch_log_group.di_endpoint_access_logs.name
  filter_pattern  = ""
  destination_arn = data.aws_kinesis_firehose_delivery_stream.dos_integration_firehose.arn
  depends_on      = [aws_cloudwatch_log_group.di_endpoint_access_logs, time_sleep.wait_a_minute]
}



resource "time_sleep" "wait_a_minute" {
  create_duration = "1m"
}
