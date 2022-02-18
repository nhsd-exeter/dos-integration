resource "aws_sns_topic" "sns_topic_app_alerts_for_slack" {

  name = var.sns_topic_app_alerts_for_slack

}

resource "aws_sns_topic_policy" "sns_topic_app_alerts_for_slack_policy" {

  arn    = aws_sns_topic.sns_topic_app_alerts_for_slack.arn
  policy = data.aws_iam_policy_document.sns_topic_app_alerts_for_slack_access.json
}

data "aws_iam_policy_document" "sns_topic_app_alerts_for_slack_access" {
  statement {
    actions = ["sns:Publish"]
    principals {
      type = "Service"
      identifiers = [
        "codestar-notifications.amazonaws.com",
        "cloudwatch.amazonaws.com"
      ]
    }
    resources = [aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  }
}

resource "aws_cloudwatch_metric_alarm" "change_event_sqs_dql_alert" {
  alarm_name                = "${var.project_id}-${var.environment}-change-event-sqs-dlq-alert"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  period                    = "1800"
  statistic                 = "Average"
  threshold                 = "0.5"
  alarm_description         = "Alert for when the Change Event SQS DQL recieves messages"
  alarm_actions             = [aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []

  dimensions = { QueueName = var.dead_letter_queue_from_fifo_queue_name }

}

resource "aws_cloudwatch_metric_alarm" "change_event_endpoint_4xx_errors_alert" {
  alarm_name                = "${var.project_id}-${var.environment}-change-event-endpoint-api-4xx-errors-alert"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "4XXError"
  namespace                 = "AWS/ApiGateway"
  period                    = "1800"
  statistic                 = "Average"
  threshold                 = "0.5"
  alarm_description         = "Alert for when the Change Event endpoint errors"
  alarm_actions             = [aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []

  dimensions = {
    ApiName = var.di_endpoint_api_gateway_name,
    Stage   = var.environment
  }

}

resource "aws_cloudwatch_metric_alarm" "change_event_endpoint_5xx_errors_alert" {
  alarm_name                = "${var.project_id}-${var.environment}-change-event-endpoint-api-5xx-errors-alert"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "5XXError"
  namespace                 = "AWS/ApiGateway"
  period                    = "1800"
  statistic                 = "Average"
  threshold                 = "0.5"
  alarm_description         = "Alert for when the Change Event endpoint errors"
  alarm_actions             = [aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []

  dimensions = {
    ApiName = var.di_endpoint_api_gateway_name,
    Stage   = var.environment
  }

}
