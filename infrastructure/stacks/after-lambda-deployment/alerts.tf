resource "aws_cloudwatch_metric_alarm" "change_event_endpoint_4xx_errors_alert" {
  alarm_name                = "${var.project_id} | ${var.environment} | DI Endpoint Errors"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "4XXError"
  namespace                 = "AWS/ApiGateway"
  period                    = "1800"
  statistic                 = "Average"
  threshold                 = "0.5"
  alarm_description         = "Change events from NHS UK have been rejected"
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []

  dimensions = {
    ApiName = var.di_endpoint_api_gateway_name,
    Stage   = var.environment
  }
}


resource "aws_cloudwatch_metric_alarm" "change_event_sqs_dlq_alert" {
  alarm_name                = "${var.project_id} | ${var.environment} | Change Events DLQ'd"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  period                    = "1800"
  statistic                 = "Average"
  threshold                 = "0.5"
  alarm_description         = "Alert for when the Change Event SQS DQL recieves messages"
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []

  dimensions = { QueueName = var.dead_letter_queue_from_fifo_queue_name }

}


resource "aws_cloudwatch_metric_alarm" "event_processor_invalid_postcode_alert" {
  alarm_name                = "${var.project_id} | ${var.environment} | Invalid Postcode"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "3"
  datapoints_to_alarm       = "2"
  threshold                 = "0"
  period                    = "300" # 5 mins
  metric_name               = "InvalidPostcode"
  namespace                 = "UEC-DOS-INT"
  statistic                 = "Sum"
  treat_missing_data        = "notBreaching"
  alarm_description         = "Events received from NHS UK with invalid postcodes"
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []
  dimensions = {
    ENV = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "event_processor_invalid_opening_times_alert" {
  alarm_name                = "${var.project_id} | ${var.environment} | Invalid Opening Times"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "3"
  datapoints_to_alarm       = "2"
  threshold                 = "0"
  period                    = "120" # 2 mins
  metric_name               = "InvalidOpenTimes"
  namespace                 = "UEC-DOS-INT"
  treat_missing_data        = "notBreaching"
  statistic                 = "Sum"
  alarm_description         = "Events received from NHS UK with invalid opening times"
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []
  dimensions = {
    ENV = var.environment
  }

}

resource "aws_cloudwatch_metric_alarm" "dos_api_unavailable" {
  alarm_name                = "${var.project_id} | ${var.environment} | DoS API Gateway Unavailable"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "3"
  datapoints_to_alarm       = "2"
  threshold                 = "0"
  period                    = "120" # 2 mins
  metric_name               = "DoSApiUnavailable"
  namespace                 = "UEC-DOS-INT"
  treat_missing_data        = "notBreaching"
  statistic                 = "Sum"
  alarm_description         = "Alert for when the DOS API Gateway Unavailable or Any Errors"
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []
  dimensions = {
    ENV = var.environment
  }

}

resource "aws_cloudwatch_metric_alarm" "change_request_to_dos_latency_alert" {
  alarm_name                = "${var.project_id} | ${var.environment} | Message Latency"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "3"
  datapoints_to_alarm       = "2"
  threshold                 = "15000"
  period                    = "600"
  metric_name               = "QueueToDoSLatency"
  namespace                 = "UEC-DOS-INT"
  statistic                 = "Average"
  alarm_description         = "Alert for when the Latency for changes request to DoS exceed a given threshold"
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []
  dimensions = {
    ENV = var.environment
  }

}


resource "aws_cloudwatch_metric_alarm" "change_request_sqs_dlq_alert" {
  alarm_name                = "${var.project_id} | ${var.environment} | Change Requests DLQ'd"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "3"
  datapoints_to_alarm       = "2"
  threshold                 = "0.5"
  period                    = "1800"
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  statistic                 = "Average"
  alarm_description         = "Alert for when the Change Request SQS DQL recieves messages"
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  insufficient_data_actions = []

  dimensions = { QueueName = var.cr_dead_letter_queue_from_fifo_queue_name }

}
