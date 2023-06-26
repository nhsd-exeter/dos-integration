#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "waf_logs" {
  name              = var.waf_log_group_name
  retention_in_days = "30"
}
