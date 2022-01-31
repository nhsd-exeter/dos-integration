resource "aws_cloudwatch_event_rule" "nightly_cron" {
  name                = var.nightly_rule_name
  description         = "Trigger performance pipeline nightly"
  schedule_expression = "cron(00 0 * * ? *)" # every day at midnight
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
  rule      = aws_cloudwatch_event_rule.nightly_cron.name
  target_id = "TriggerPerformancePipeline"
  arn       = aws_codepipeline.codepipeline.arn
  role_arn  = aws_iam_role.performance_rule_role.arn
}

resource "aws_iam_role" "performance_rule_role" {
  name = "${var.project_id}-${var.environment}-performance-rule-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}
