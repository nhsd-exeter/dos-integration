resource "aws_cloudwatch_metric_alarm" "waf_ip_allow_list_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF IP Allow List Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF IP Allow List Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_ip_allow_list_rule_name,
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}

resource "aws_cloudwatch_metric_alarm" "waf_ip_rate_limit_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF Rate Limit Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF Rate Limit Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_rate_based_rule_name,
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}

resource "aws_cloudwatch_metric_alarm" "waf_aws_managed_rules_common_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF AWS Managed Rules Common Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF AWS Managed Rules Common Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_aws_common_rule_name,
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}

resource "aws_cloudwatch_metric_alarm" "waf_non_gb_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF Non GB Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF Non GB Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_non_gb_rule_name,
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}

resource "aws_cloudwatch_metric_alarm" "waf_aws_managed_known_bad_inputs_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF AWS Managed Known Bad Inputs Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF AWS Managed Known Bad Inputs Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_aws_known_bad_inputs_rule_name,
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}

resource "aws_cloudwatch_metric_alarm" "waf_aws_managed_sql_injection_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF AWS Managed SQL Injection Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF AWS Managed SQL Injection Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_aws_sqli_rule_name,
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}

resource "aws_cloudwatch_metric_alarm" "waf_custom_sql_injection_count_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF Custom SQL Injection Count Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF Custom SQL Injection Count Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_custom_sqli_rule_name
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "CountedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}

resource "aws_cloudwatch_metric_alarm" "waf_aws_managed_ip_reputation_list_blocked_requests" {
  count               = var.waf_enabled ? 1 : 0
  alarm_actions       = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description   = "WAF AWS Managed IP Reputation List Blocked Requests"
  alarm_name          = "${var.project_id} | ${var.shared_environment} | WAF AWS Managed IP Reputation List Blocked Requests"
  comparison_operator = "GreaterThanThreshold"
  datapoints_to_alarm = "1"
  dimensions = {
    Rule   = var.waf_ip_reputation_list_rule_name,
    WebACL = var.waf_acl_name,
    Region = var.aws_region
  }
  evaluation_periods = "1"
  metric_name        = "BlockedRequests"
  namespace          = "AWS/WAFV2"
  period             = "60"
  statistic          = "Sum"
  threshold          = "1"
}
