resource "aws_cloudwatch_metric_alarm" "service_matcher_invalid_postcode_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Events received from NHS UK with invalid postcodes"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Invalid Postcode"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "InvalidPostcode"
  namespace                 = "UEC-DOS-INT"
  period                    = "60" #1 min
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "service_matcher_invalid_opening_times_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Events received from NHS UK with invalid opening times"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Invalid Opening Times"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "InvalidOpenTimes"
  namespace                 = "UEC-DOS-INT"
  period                    = "60" # 1 min
  statistic                 = "Sum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "holiding_sqs_dlq_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the Holding Queue Message DLQ has recieved messages"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Holding Queue Message DLQ'd"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { QueueName = var.holding_queue_dlq }
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
  alarm_description         = "Alert for when the Update Request DLQ has recieved messages"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Update Requests DLQ'd"
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
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DB has too many connections"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | High DB Connections"
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
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}

resource "aws_cloudwatch_metric_alarm" "dos_db_replica_db_connections_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DI Replica DB has too many connections"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | High DB Replica Connections"
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
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}

resource "aws_cloudwatch_metric_alarm" "dos_db_cpu_utilisation_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DB has too high CPU Utilisation"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | High DB CPU Utilisation"
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
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}

resource "aws_cloudwatch_metric_alarm" "dos_db_replica_cpu_utilisation_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DoS DI Replica DB has too high CPU Utilisation"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | High DB Replica CPU Utilisation"
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
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}


resource "aws_cloudwatch_metric_alarm" "high_number_of_change_events_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert when the DI has recieved a high number of change events"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | High Number of Change Events received"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "ChangeEventReceived"
  namespace                 = "UEC-DOS-INT"
  period                    = "300"
  statistic                 = "Sum"
  threshold                 = "1500"
  treat_missing_data        = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "high_number_of_update_requests_waiting_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is waiting to process update requests in service sync"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Update Requests Waiting"
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

resource "aws_cloudwatch_metric_alarm" "high_number_of_failed_emails_alert" {
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is failing to send emails"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Failed Emails"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "EmailFailed"
  namespace                 = "UEC-DOS-INT"
  period                    = "120" # 2 minutes
  statistic                 = "Sum"
  threshold                 = "1"
}

resource "aws_cloudwatch_metric_alarm" "high_number_emails_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is sending many emails"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | High Number of Emails Sent"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "EmailSent"
  namespace                 = "UEC-DOS-INT"
  period                    = "86400" # 1 Day
  statistic                 = "Sum"
  threshold                 = "2"
}

resource "aws_cloudwatch_metric_alarm" "average_message_latency_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the Latency for when changes are taken to long to process and save"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Average Message Latency"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "2"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "6"
  insufficient_data_actions = []
  metric_name               = "QueueToDoSLatency"
  namespace                 = "UEC-DOS-INT"
  period                    = "300"
  statistic                 = "Average"
  threshold                 = "120000" # 2 Minutes
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}

resource "aws_cloudwatch_metric_alarm" "maximum_message_latency_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when DI is taking longer than expected to process update requests"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Maximum Message Latency"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "2"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "6"
  insufficient_data_actions = []
  metric_name               = "QueueToDoSLatency"
  namespace                 = "UEC-DOS-INT"
  period                    = "300"
  statistic                 = "Maximum"
  threshold                 = "120000" # 2 Minutes
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}

resource "aws_cloudwatch_metric_alarm" "dos_palliative_care_z_code_does_not_exist" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the DoS Palliative Care Z Code does not exist"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | DoS Palliative Care Z Code Does Not Exist !!!"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "DoSPalliativeCareZCodeDoesNotExist"
  namespace                 = "UEC-DOS-INT"
  period                    = "60"
  statistic                 = "Maximum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}

resource "aws_cloudwatch_metric_alarm" "dos_blood_pressure_z_code_does_not_exist" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Alert for when the DoS Blood Pressure Z Code does not exist"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | DoS Blood Pressure Z Code Does Not Exist !!!"
  comparison_operator       = "GreaterThanThreshold"
  datapoints_to_alarm       = "1"
  dimensions                = { ENV = var.blue_green_environment }
  evaluation_periods        = "1"
  insufficient_data_actions = []
  metric_name               = "DoSBloodPressureZCodeDoesNotExist"
  namespace                 = "UEC-DOS-INT"
  period                    = "60"
  statistic                 = "Maximum"
  threshold                 = "0"
  treat_missing_data        = "notBreaching"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
}
