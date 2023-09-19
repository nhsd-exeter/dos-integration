resource "aws_cloudwatch_metric_alarm" "di_endpoint_endpoint_4xx_errors_alert" {
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "Change events from NHS UK have been rejected"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | DI 4XX Endpoint Errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    ApiName = var.di_endpoint_api_gateway_name,
    Stage   = var.shared_environment
  }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "4XXError"
  namespace                 = "AWS/ApiGateway"
  period                    = "60"
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
  depends_on = [
    aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region
  ]
}

resource "aws_cloudwatch_metric_alarm" "di_endpoint_endpoint_5xx_errors_alert" {
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "Change events from NHS UK have been rejected"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | DI 5XX Endpoint Errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    ApiName = var.di_endpoint_api_gateway_name,
    Stage   = var.shared_environment
  }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "5XXError"
  namespace                 = "AWS/ApiGateway"
  period                    = "60"
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
  depends_on = [
    aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region
  ]
}

resource "aws_cloudwatch_metric_alarm" "change_event_sqs_dlq_alert" {
  alarm_actions             = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the Change Event DLQ has recieved messages"
  alarm_name                = "${var.project_id} | ${var.shared_environment} | Change Events DLQ'd"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { QueueName = var.change_event_dlq }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  period                    = "60"
  statistic                 = "Sum"
  threshold                 = "0"
}

resource "aws_cloudwatch_metric_alarm" "high_number_of_change_events_waiting_alert" {
  alarm_actions             = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is waiting to process change events in service matcher"
  alarm_name                = "${var.project_id} | ${var.shared_environment} | Change Events Waiting"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "2"
  dimensions                = { ENV = var.change_event_queue_name }
  evaluation_periods        = "3"
  insufficient_data_actions = []
  metric_name               = "ApproximateNumberOfMessagesDelayed"
  namespace                 = "AWS/SQS"
  period                    = "300"
  statistic                 = "Average"
  threshold                 = "60000" # 60 Seconds
  depends_on = [
    aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region
  ]
}

resource "aws_cloudwatch_metric_alarm" "di_endpoint_health_check_alarm" {
  provider                  = aws.route53_health_check_alarm_region
  alarm_actions             = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn]
  alarm_description         = "Alert for when DI endpoint is failing Route53 health checks"
  alarm_name                = "${var.project_id} | ${var.shared_environment} | DI Endpoint Route 53 Health Checks Failing"
  comparison_operator       = "LessThanThreshold"
  dimensions                = { HealthCheckId = aws_route53_health_check.di_endpoint_health_check.id }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "HealthCheckStatus"
  namespace                 = "AWS/Route53"
  period                    = "60" # 1 minute
  statistic                 = "Average"
  threshold                 = "1"

  depends_on = [
    aws_route53_health_check.di_endpoint_health_check, aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region
  ]
}
