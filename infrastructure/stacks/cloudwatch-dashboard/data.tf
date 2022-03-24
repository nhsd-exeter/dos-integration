data "aws_sns_topic" "sns_topic_app_alerts_for_slack" {
  name = var.sns_topic_app_alerts_for_slack
}
