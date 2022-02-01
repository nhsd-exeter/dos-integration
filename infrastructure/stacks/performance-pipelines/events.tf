resource "aws_cloudwatch_event_rule" "stress_test_cron" {
  name                = "${var.project_id}-${var.environment}-stress-test-trigger"
  description         = "Trigger performance pipeline nightly"
  schedule_expression = "cron(00 0 * * ? *)" # every Monday at midnight
}

resource "aws_cloudwatch_event_target" "trigger_stress_test_pipeline" {
  rule      = aws_cloudwatch_event_rule.stress_test_cron.name
  target_id = "TriggerStressTestPipeline"
  arn       = aws_codepipeline.stress_test_codepipeline.arn
  role_arn  = aws_iam_role.performance_rule_role.arn
}

resource "aws_cloudwatch_event_rule" "load_test_cron" {
  name                = "${var.project_id}-${var.environment}-load-test-trigger"
  description         = "Trigger performance pipeline nightly"
  schedule_expression = "cron(00 0 * * ? *)" # every Tuesday at midnight
}

resource "aws_cloudwatch_event_target" "trigger_load_test_pipeline" {
  rule      = aws_cloudwatch_event_rule.load_test_cron.name
  target_id = "TriggerloadTestPipeline"
  arn       = aws_codepipeline.load_test_codepipeline.arn
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
