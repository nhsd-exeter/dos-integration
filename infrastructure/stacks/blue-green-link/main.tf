# ##############
# # SQS Subscriptions
# ##############
resource "aws_lambda_event_source_mapping" "change_event_event_source_mapping" {
  batch_size       = 1
  event_source_arn = data.aws_sqs_queue.change_event_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.ingest_change_event.arn
}

resource "aws_lambda_event_source_mapping" "change_event_dlq_event_source_mapping" {
  batch_size       = 1
  event_source_arn = data.aws_sqs_queue.change_event_dlq.arn
  enabled          = true
  function_name    = data.aws_lambda_function.change_event_dlq_handler.arn
}

# ##############
# # SNS Subscriptions
# ##############

resource "aws_sns_topic_subscription" "shared_resources_sns_topic_app_alerts_for_slack_default_region_subscription" {
  topic_arn = data.aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_messenger.arn
}

resource "aws_sns_topic_subscription" "shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region_subscription" {
  provider  = aws.route53_health_check_alarm_region
  topic_arn = data.aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_messenger.arn
}

resource "aws_lambda_permission" "allow_sns_from_shared_resources_sns_topic_app_alerts_for_slack_default_region_subscription" {
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_messenger.arn
  principal     = "sns.amazonaws.com"
  source_arn    = data.aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn
}

resource "aws_lambda_permission" "allow_sns_from_shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region_subscription" {
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_messenger.arn
  principal     = "sns.amazonaws.com"
  source_arn    = data.aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn
}
