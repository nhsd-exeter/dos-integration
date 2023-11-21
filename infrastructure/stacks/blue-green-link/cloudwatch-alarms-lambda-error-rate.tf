resource "aws_cloudwatch_metric_alarm" "change_event_dlq_handler_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Change Event DLQ Handler error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Change Event DLQ Handler Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.change_event_dlq_handler_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.change_event_dlq_handler_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "dos_db_update_dlq_handler_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "DoS DB Update DLQ Handler error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | DoS DB Update DLQ Handler Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.dos_db_update_dlq_handler_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.dos_db_update_dlq_handler_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "event_replay_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Event Replay error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Event Replay Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.event_replay_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.event_replay_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "ingest_change_event_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Ingest Change Event error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Ingest Change Event Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.ingest_change_event_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.ingest_change_event_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "send_email_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Send Email error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Send Email Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.send_email_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.send_email_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "service_matcher_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Service Matcher error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Service Matcher Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.service_matcher_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.service_matcher_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "service_sync_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Service Sync error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Service Sync Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.service_sync_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.service_sync_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "slack_messenger_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Slack Messenger error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Slack Messenger Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.slack_messenger_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.slack_messenger_lambda
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "quality_checker_error_rate_alert" {
  count                     = var.profile == "dev" ? 0 : 1
  alarm_actions             = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  alarm_description         = "Quality Checker error rate has exceeded 1%"
  alarm_name                = "${var.project_id} | ${var.blue_green_environment} | Quality Checker Error Rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  threshold                 = "1"
  insufficient_data_actions = []
  treat_missing_data        = "missing"
  ok_actions                = [data.aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]

  metric_query {
    id          = "expression"
    expression  = "(errors/invocations) * 100"
    label       = "Error Rate (%)"
    return_data = "true"
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.quality_checker_lambda
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = "120"
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        FunctionName = var.slack_messenger_lambda
      }
    }
  }
}
