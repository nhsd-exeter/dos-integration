resource "aws_sns_topic" "sns_topic_app_alerts_for_slack_default_region" {
  name              = var.sns_topic_app_alerts_for_slack_default_region
  kms_master_key_id = "alias/${var.signing_key_alias}"
}

resource "aws_sns_topic_policy" "sns_topic_app_alerts_for_slack_policy_default_region" {
  arn    = aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn
  policy = data.aws_iam_policy_document.sns_topic_app_alerts_for_slack_access_default_region.json
  depends_on = [
    data.aws_iam_policy_document.sns_topic_app_alerts_for_slack_access_default_region
  ]
}

resource "aws_sns_topic_subscription" "sns_topic_app_alerts_for_slack_policy_default_region_subscription" {
  topic_arn  = aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn
  protocol   = "lambda"
  endpoint   = module.slack_messenger_lambda.lambda_function_arn
  depends_on = [aws_sns_topic.sns_topic_app_alerts_for_slack_default_region, aws_sns_topic_policy.sns_topic_app_alerts_for_slack_policy_default_region]
}

resource "aws_lambda_permission" "allow_sns_topic_app_alerts_for_slack_policy_default_region_subscription" {
  action        = "lambda:InvokeFunction"
  function_name = module.slack_messenger_lambda.lambda_function_arn
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn
}

resource "aws_sns_topic" "sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  provider          = aws.route53_health_check_alarm_region
  name              = var.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region
  kms_master_key_id = "alias/${var.route53_health_check_alarm_region_signing_key_alias}"
}

resource "aws_sns_topic_policy" "sns_topic_app_alerts_for_slack_policy_alarm_region" {
  provider = aws.route53_health_check_alarm_region
  arn      = aws_sns_topic.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn
  policy   = data.aws_iam_policy_document.sns_topic_app_alerts_for_slack_access_alarm_region.json
  depends_on = [
    data.aws_iam_policy_document.sns_topic_app_alerts_for_slack_access_alarm_region
  ]
}

resource "aws_sns_topic_subscription" "sns_topic_app_alerts_for_slack_route53_health_check_alarm_region_subscription" {
  provider   = aws.route53_health_check_alarm_region
  topic_arn  = aws_sns_topic.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn
  protocol   = "lambda"
  endpoint   = module.slack_messenger_lambda.lambda_function_arn
  depends_on = [aws_sns_topic.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region, aws_sns_topic_policy.sns_topic_app_alerts_for_slack_policy_alarm_region]
}

resource "aws_lambda_permission" "allow_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region_subscription" {
  action        = "lambda:InvokeFunction"
  function_name = module.slack_messenger_lambda.lambda_function_arn
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn
}
