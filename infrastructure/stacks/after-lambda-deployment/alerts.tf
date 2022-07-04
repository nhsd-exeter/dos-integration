resource "aws_cloudwatch_metric_alarm" "change_event_endpoint_4xx_errors_alert" {
  alarm_actions       = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description   = "Change events from NHS UK have been rejected"
  alarm_name          = "${var.project_id} | ${var.environment} | DI Endpoint Errors"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    ApiName = var.di_endpoint_api_gateway_name,
    Stage   = var.environment
  }
  evaluation_periods        = "2"
  insufficient_data_actions = []
  metric_name               = "4XXError"
  namespace                 = "AWS/ApiGateway"
  period                    = "60"
  statistic                 = "Average"
  threshold                 = "1"
  treat_missing_data        = "notBreaching"
}


resource "aws_cloudwatch_metric_alarm" "event_processor_invalid_postcode_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description         = "Events received from NHS UK with invalid postcodes"
  alarm_name                = "${var.project_id} | ${var.environment} | Invalid Postcode"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "InvalidPostcode"
  namespace                 = "UEC-DOS-INT"
  period                    = "120" # 2 min
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "event_processor_invalid_opening_times_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description         = "Events received from NHS UK with invalid opening times"
  alarm_name                = "${var.project_id} | ${var.environment} | Invalid Opening Times"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "InvalidOpenTimes"
  namespace                 = "UEC-DOS-INT"
  period                    = "120" # 2 min
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "dos_api_unavailable" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description         = "Alert for when the DOS API Gateway Unavailable or Any Errors"
  alarm_name                = "${var.project_id} | ${var.environment} | DoS API Gateway Unavailable"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "2"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "2"
  insufficient_data_actions = []
  metric_name               = "DoSApiUnavailable"
  namespace                 = "UEC-DOS-INT"
  period                    = "60" # 1 min
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "change_request_to_dos_latency_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description         = "Alert for when the Latency for changes request to DoS exceed a given threshold"
  alarm_name                = "${var.project_id} | ${var.environment} | Message Latency"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "2"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "3"
  insufficient_data_actions = []
  metric_name               = "QueueToDoSLatency"
  namespace                 = "UEC-DOS-INT"
  period                    = "600"
  statistic                 = "Average"
  threshold                 = "30000" # 30 Seconds
}

resource "aws_cloudwatch_metric_alarm" "change_event_sqs_dlq_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description         = "Alert for when the Change Event SQS DQL recieves messages"
  alarm_name                = "${var.project_id} | ${var.environment} | Change Events DLQ'd"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { QueueName = var.dead_letter_queue_from_fifo_queue_name }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  period                    = "60"
  statistic                 = "Sum"
  threshold                 = "0"
}

resource "aws_cloudwatch_metric_alarm" "change_request_sqs_dlq_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description         = "Alert for when the Change Request SQS DQL recieves messages"
  alarm_name                = "${var.project_id} | ${var.environment} | Change Requests DLQ'd"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { QueueName = var.cr_dead_letter_queue_from_fifo_queue_name }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  period                    = "60"
  statistic                 = "Sum"
  threshold                 = "0"
}

resource "aws_cloudwatch_metric_alarm" "dos_api_gateway_400_error_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  alarm_description         = "Alert for when the DoS API Gateway returns a 400 error"
  alarm_name                = "${var.project_id} | ${var.environment} | DoS API Gateway 400 Error"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { QueueName = var.cr_dead_letter_queue_from_fifo_queue_name }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  period                    = "60"
  statistic                 = "Sum"
  threshold                 = "0"
}
