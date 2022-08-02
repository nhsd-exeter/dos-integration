resource "aws_cloudwatch_query_definition" "errors" {
  name = "${var.project_id}/${var.environment}/errors"

  log_group_names = [
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| parse response_text '"detail":"*"' as dos_error
| filter level == 'ERROR'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "by_correlation_id" {
  name = "${var.project_id}/${var.environment}/by-correlation-id"

  log_group_names = [
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter correlation_id == 'REPLACE'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "by_correlation_id_simple" {
  name = "${var.project_id}/${var.environment}/by-correlation-id-simple"

  log_group_names = [
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp, message
| filter correlation_id == 'REPLACE'
| sort @timestamp
EOF
}


resource "aws_cloudwatch_query_definition" "by_invalid_postcode" {
  name = "${var.project_id}/${var.environment}/by-invalid-postcode"

  log_group_names = [
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter report_key == 'INVALID_POSTCODE'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "by_invalid_opening_times" {
  name = "${var.project_id}/${var.environment}/by-invalid-opening-times"

  log_group_names = [
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter report_key == 'INVALID_OPEN_TIMES'
| sort @timestamp
EOF
}
