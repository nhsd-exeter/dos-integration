resource "aws_cloudwatch_metric_alarm" "change_event_endpoint_4xx_errors_alert" {
  alarm_actions       = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
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
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}


resource "aws_cloudwatch_metric_alarm" "service_matcher_invalid_postcode_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Events received from NHS UK with invalid postcodes"
  alarm_name                = "${var.project_id} | ${var.environment} | Invalid Postcode"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "InvalidPostcode"
  namespace                 = "UEC-DOS-INT"
  period                    = "240" # 2 min
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "service_matcher_invalid_opening_times_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Events received from NHS UK with invalid opening times"
  alarm_name                = "${var.project_id} | ${var.environment} | Invalid Opening Times"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "InvalidOpenTimes"
  namespace                 = "UEC-DOS-INT"
  period                    = "240" # 4 min
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "message_latency_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the Latency for when changes are taken to long to process and save"
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
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the Change Event DQL has recieved messages"
  alarm_name                = "${var.project_id} | ${var.environment} | Change Events DLQ'd"
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

resource "aws_cloudwatch_metric_alarm" "update_request_dlq_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the Update Request DQL has recieved messages"
  alarm_name                = "${var.project_id} | ${var.environment} | Update Requests DLQ'd"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { QueueName = var.update_request_dlq }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "NumberOfMessagesReceived"
  namespace                 = "AWS/SQS"
  period                    = "60"
  statistic                 = "Sum"
  threshold                 = "0"
}

resource "aws_cloudwatch_metric_alarm" "dos_db_db_connections_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DB has too many connections"
  alarm_name                = "${var.project_id} | ${var.environment} | High DB Connections"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { DBInstanceIdentifier = var.dos_db_name }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "DatabaseConnections"
  namespace                 = "AWS/RDS"
  period                    = "60"
  statistic                 = "Maximum"
  threshold                 = "250"
}

resource "aws_cloudwatch_metric_alarm" "dos_db_replica_db_connections_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DI Replica DB has too many connections"
  alarm_name                = "${var.project_id} | ${var.environment} | High DB Replica Connections"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { DBInstanceIdentifier = var.dos_db_replica_name }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "DatabaseConnections"
  namespace                 = "AWS/RDS"
  period                    = "60"
  statistic                 = "Maximum"
  threshold                 = "250"
}

resource "aws_cloudwatch_metric_alarm" "dos_db_cpu_utilisation_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DB has too high CPU Utilisation"
  alarm_name                = "${var.project_id} | ${var.environment} | High DB CPU Utilisation"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { DBInstanceIdentifier = var.dos_db_name }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "CPUUtilization"
  namespace                 = "AWS/RDS"
  period                    = "60"
  statistic                 = "Maximum"
  threshold                 = "70"
}

resource "aws_cloudwatch_metric_alarm" "dos_db_replica_cpu_utilisation_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DI Replica DB has too high CPU Utilisation"
  alarm_name                = "${var.project_id} | ${var.environment} | High DB Replica CPU Utilisation"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { DBInstanceIdentifier = var.dos_db_replica_name }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "CPUUtilization"
  namespace                 = "AWS/RDS"
  period                    = "60"
  statistic                 = "Maximum"
  threshold                 = "70"
}


# resource "aws_cloudwatch_metric_alarm" "dos_db_replica_lag_alert" {
#   alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
#   alarm_description         = "Alert when the DoS DI Replica DB has too lag from the primary DoS DB"
#   alarm_name                = "${var.project_id} | ${var.environment} | Replica Lag Very High"
#   comparison_operator       = "GreaterThanThreshold"
#   datapoints_to_alarm       = "1"
#   dimensions                = { DBInstanceIdentifier = var.dos_db_replica_name }
#   evaluation_periods        = "1"
#   insufficient_data_actions = []
#   metric_name               = "ReplicaLag"
#   namespace                 = "AWS/RDS"
#   period                    = "60"
#   statistic                 = "Average"
#   threshold                 = "300"
# }


resource "aws_cloudwatch_metric_alarm" "high_number_of_change_events_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DI has recieved a high number of change events"
  alarm_name                = "${var.project_id} | ${var.environment} | High Number of Change Events received"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "ChangeEventReceived"
  namespace                 = "UEC-DOS-INT"
  period                    = "300"
  statistic                 = "Sum"
  threshold                 = "800"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "high_number_of_change_events_waiting_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is waiting to process change events in service matcher"
  alarm_name                = "${var.project_id} | ${var.environment} | Change Events Waiting"
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
}

resource "aws_cloudwatch_metric_alarm" "high_number_of_update_requests_waiting_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is waiting to process update requests in service sync"
  alarm_name                = "${var.project_id} | ${var.environment} | Update Requests Waiting"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "2"
  dimensions                = { ENV = var.update_request_queue_name }
  evaluation_periods        = "3"
  insufficient_data_actions = []
  metric_name               = "ApproximateNumberOfMessagesDelayed"
  namespace                 = "AWS/SQS"
  period                    = "600"
  statistic                 = "Average"
  threshold                 = "30000" # 30 Seconds
}

resource "aws_cloudwatch_metric_alarm" "health_check_failures_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DB or Replica is likely down or unaccessible and found by too many health check failures"
  alarm_name                = "${var.project_id} | ${var.environment} | High Health Check Failures"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "ServiceSyncHealthCheckFailure"
  namespace                 = "UEC-DOS-INT"
  period                    = "120" # 2 minutes
  statistic                 = "Sum"
  threshold                 = "2"
}

resource "aws_cloudwatch_metric_alarm" "high_number_of_failed_emails_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is failing to send emails"
  alarm_name                = "${var.project_id} | ${var.environment} | Failed Emails"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "EmailFailed"
  namespace                 = "UEC-DOS-INT"
  period                    = "120" # 2 minutes
  statistic                 = "Sum"
  threshold                 = "1"
}

resource "aws_cloudwatch_metric_alarm" "high_number_emails_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is failing to send emails"
  alarm_name                = "${var.project_id} | ${var.environment} | High Number of Emails Sent"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  dimensions                = { ENV = var.environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "EmailSent"
  namespace                 = "UEC-DOS-INT"
  period                    = "86400" # 1 Day
  statistic                 = "Sum"
  threshold                 = "2"
}

resource "aws_cloudwatch_metric_alarm" "di_endpoint_health_check_alarm" {
  provider                  = aws.alarm-region
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_alarm_region.arn]
  alarm_description         = "Alert for when DI endpoint is failing Route53 health checks"
  alarm_name                = "${var.project_id} | ${var.environment} | DI Endpoint Route 53 Health Checks Failing"
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
    aws_route53_health_check.di_endpoint_health_check
  ]
}
