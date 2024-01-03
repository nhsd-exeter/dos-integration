resource "aws_cloudwatch_event_rule" "quality_checker_schedule" {
  name                = var.quality_checker_lambda_schedule_name
  description         = "Trigger the quality checker lambda on a weekly schedule"
  schedule_expression = "cron(30 4 ? * MON *)"
}

resource "aws_cloudwatch_event_target" "quality_checker_schedule_trigger" {
  rule = aws_cloudwatch_event_rule.quality_checker_schedule.name
  arn  = data.aws_lambda_function.quality_checker.arn
}
