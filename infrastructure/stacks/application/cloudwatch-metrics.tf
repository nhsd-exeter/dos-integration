resource "aws_cloudwatch_log_metric_filter" "change_event_dlq_handler_received_event" {
  name           = "${var.project_id}-${var.blue_green_environment}-change-event-dlq-handler-received-event"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"ChangeEventsDLQHandlerReceivedEvent\" }"
  log_group_name = module.change_event_dlq_handler_lambda.lambda_cloudwatch_log_group_name


  metric_transformation {
    name      = "ChangeEventsDLQHandlerReceivedEvent"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "dos_db_update_dlq_handler_received_event" {
  name           = "${var.project_id}-${var.blue_green_environment}-dos-db-update-dlq-handler-received-event"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"DoSDBUpdateDLQHandlerReceivedEvent\" }"
  log_group_name = module.dos_db_update_dlq_handler_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "DoSDBUpdateDLQHandlerReceivedEvent"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "change_event_received" {
  name           = "${var.project_id}-${var.blue_green_environment}-change-event-received"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"ChangeEventReceived\" }"
  log_group_name = module.ingest_change_event_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "ChangeEventReceived"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "quality_checker_issue_found" {
  name           = "${var.project_id}-${var.blue_green_environment}-quality-checker-issue-found"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"QualityCheckerIssueFound\" }"
  log_group_name = module.quality_checker_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "QualityCheckerIssueFound"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "quality_checker_finished" {
  name           = "${var.project_id}-${var.blue_green_environment}-quality-checker-finished"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"QualityCheckerFinished\" }"
  log_group_name = module.quality_checker_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "QualityCheckerFinished"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "quality_checker_errored" {
  name           = "${var.project_id}-${var.blue_green_environment}-quality-checker-errored"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"QualityCheckerErrored\" }"
  log_group_name = module.quality_checker_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "QualityCheckerErrored"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "email_sent" {
  name           = "${var.project_id}-${var.blue_green_environment}-email-sent"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"EmailSent\" }"
  log_group_name = module.send_email_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "EmailSent"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "email_failed" {
  name           = "${var.project_id}-${var.blue_green_environment}-email-failed"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"EmailFailed\" }"
  log_group_name = module.send_email_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "EmailFailed"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "invalid_open_times" {
  name           = "${var.project_id}-${var.blue_green_environment}-invalid-open-times"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"InvalidOpenTimes\" }"
  log_group_name = module.service_matcher_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "InvalidOpenTimes"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "invalid_postcode" {
  name           = "${var.project_id}-${var.blue_green_environment}-invalid-postcode"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"InvalidPostcode\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "InvalidPostcode"
    namespace = "uec-dos-int"
    value     = "1"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "dos_specific_service_update" {
  name           = "${var.project_id}-${var.blue_green_environment}-dos-specific-service-update"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"ServiceUpdate\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "DoSServiceUpdate"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
      field       = "$.data_field_modified"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "dos_all_service_update" {
  name           = "${var.project_id}-${var.blue_green_environment}-dos-all-service-update"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"ServiceUpdate\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "DoSAllServiceUpdates"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "update_request_sent" {
  name           = "${var.project_id}-${var.blue_green_environment}-update-request-sent"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"UpdateRequestSent\" }"
  log_group_name = module.service_matcher_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "UpdateRequestSent"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "update_request_success" {
  name           = "${var.project_id}-${var.blue_green_environment}-update-request-success"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"UpdateRequestSuccess\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "UpdateRequestSuccess"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "update_request_failed" {
  name           = "${var.project_id}-${var.blue_green_environment}-update-request-failed"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"UpdateRequestError\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "UpdateRequestFailed"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "queue_to_dos_latency" {
  name           = "${var.project_id}-${var.blue_green_environment}-queue-to-dos-latency"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"UpdateRequestSuccess\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "QueueToDoSLatency"
    namespace = "uec-dos-int"
    value     = "$.latency"
    unit      = "Milliseconds"
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "dos_palliative_care_z_code_does_not_exist" {
  name           = "${var.project_id}-${var.blue_green_environment}-dos-palliative-care-z-code-does-not-exist"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"DoSPalliativeCareZCodeDoesNotExist\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "DoSPalliativeCareZCodeDoesNotExist"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
    }
  }
}


resource "aws_cloudwatch_log_metric_filter" "dos_blood_pressure_z_code_does_not_exist" {
  name           = "${var.project_id}-${var.blue_green_environment}-dos-blood-pressure-z-code-does-not-exist"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"BloodPressureZCodeDoesNotExist\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "DoSBloodPressureZCodeDoesNotExist"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "dos_contraception_z_code_does_not_exist" {
  name           = "${var.project_id}-${var.blue_green_environment}-dos-contraception-z-code-does-not-exist"
  pattern        = "{ $.cloudwatch_metric_filter_matching_attribute = \"ContraceptionZCodeDoesNotExist\" }"
  log_group_name = module.service_sync_lambda.lambda_cloudwatch_log_group_name

  metric_transformation {
    name      = "DoSContraceptionZCodeDoesNotExist"
    namespace = "uec-dos-int"
    value     = 1
    dimensions = {
      environment = "$.environment"
    }
  }
}
