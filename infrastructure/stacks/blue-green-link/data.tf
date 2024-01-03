# ##############
# # LAMBDA
# ##############

data "aws_lambda_function" "ingest_change_event" {
  function_name = var.ingest_change_event_lambda
}

data "aws_lambda_function" "slack_messenger" {
  function_name = var.slack_messenger_lambda
}

data "aws_lambda_function" "change_event_dlq_handler" {
  function_name = var.change_event_dlq_handler_lambda
}

data "aws_lambda_function" "quality_checker" {
  function_name = var.quality_checker_lambda
}

# ##############
# # SQS
# ##############

data "aws_sqs_queue" "change_event_queue" {
  name = var.change_event_queue
}

data "aws_sqs_queue" "change_event_dlq" {
  name = var.change_event_dlq
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

data "aws_sns_topic" "sns_topic_app_alerts_for_slack_default_region" {
  name = var.sns_topic_app_alerts_for_slack_default_region
}

data "aws_sns_topic" "sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  provider = aws.route53_health_check_alarm_region
  name     = var.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region
}
