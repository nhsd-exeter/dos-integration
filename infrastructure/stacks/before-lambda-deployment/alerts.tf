resource "aws_sns_topic" "sns_topic_app_alerts_for_slack" {
  name              = var.sns_topic_app_alerts_for_slack
  kms_master_key_id = "alias/${var.signing_key_alias}"
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
        "cloudwatch.amazonaws.com",
        "codestar-notifications.amazonaws.com"
      ]
    }
    resources = [aws_sns_topic.sns_topic_app_alerts_for_slack.arn]
  }
}
