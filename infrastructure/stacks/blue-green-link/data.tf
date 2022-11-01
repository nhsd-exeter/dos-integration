# ##############
# # LAMBDA
# ##############

data "aws_lambda_function" "ingest_change_event" {
  function_name = var.ingest_change_event_lambda_name
}

data "aws_lambda_function" "slack_messenger" {
  function_name = var.slack_messenger_lambda_name
}

data "aws_lambda_function" "change_event_dlq_handler" {
  function_name = var.change_event_dlq_handler_lambda_name
}

# ##############
# # SQS
# ##############

data "aws_sqs_queue" "change_event_queue" {
  name = var.change_event_queue_name
}

data "aws_sqs_queue" "shared_resources_dlq" {
  name = var.shared_resources_dlq
}

# ##############
# # SNS
# ##############

data "aws_sns_topic" "shared_resources_sns_topic_app_alerts_for_slack_default_region" {
  name = var.shared_resources_sns_topic_app_alerts_for_slack_default_region
}

data "aws_sns_topic" "shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  provider = aws.route53_health_check_alarm_region
  name     = var.shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region
}
