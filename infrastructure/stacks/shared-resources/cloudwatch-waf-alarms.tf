resource "aws_cloudwatch_metric_alarm" "waf_ip_allow_list_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF IP Allow List Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF IP Allow List Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_ip_allow_list_rule_name,
    WebACL = var.waf_acl_name
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "0"
  treat_missing_data = "notBreaching"
}
