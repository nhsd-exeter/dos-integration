resource "aws_cloudwatch_query_definition" "search_for_errors" {
  name = "${var.project_id}/${var.blue_green_environment}/search-for-errors"

  log_group_names = [
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}",
    "/aws/lambda/${var.ingest_change_event_lambda_name}",
    "/aws/lambda/${var.send_email_lambda_name}",
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp, correlation_id, ods_code, function_name, message
| filter level == 'ERROR'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "search_by_correlation_id" {
  name = "${var.project_id}/${var.blue_green_environment}/search-by-correlation-id"

  log_group_names = [
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}",
    "/aws/lambda/${var.ingest_change_event_lambda_name}",
    "/aws/lambda/${var.send_email_lambda_name}",
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter correlation_id == 'REPLACE'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "search_by_correlation_id_simple" {
  name = "${var.project_id}/${var.blue_green_environment}/search-by-correlation-id-simple"

  log_group_names = [
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}",
    "/aws/lambda/${var.ingest_change_event_lambda_name}",
    "/aws/lambda/${var.send_email_lambda_name}",
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp, message
| filter correlation_id == 'REPLACE'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "search_by_odscode" {
  name = "${var.project_id}/${var.blue_green_environment}/search-by-odscode"

  log_group_names = [
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}",
    "/aws/lambda/${var.ingest_change_event_lambda_name}",
    "/aws/lambda/${var.send_email_lambda_name}",
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter ods_code == 'REPLACE'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "search_by_odscode_simple" {
  name = "${var.project_id}/${var.blue_green_environment}/search-by-odscode-simple"

  log_group_names = [
    "/aws/lambda/${var.change_event_dlq_handler_lambda_name}",
    "/aws/lambda/${var.dos_db_update_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}",
    "/aws/lambda/${var.ingest_change_event_lambda_name}",
    "/aws/lambda/${var.send_email_lambda_name}",
    "/aws/lambda/${var.service_matcher_lambda_name}",
    "/aws/lambda/${var.service_sync_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp, message
| filter ods_code == 'REPLACE'
| sort @timestamp
EOF
}


resource "aws_cloudwatch_query_definition" "search_for_invalid_postcode" {
  name = "${var.project_id}/${var.blue_green_environment}/search-for-invalid-postcode"

  log_group_names = [
    "/aws/lambda/${var.service_sync_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter report_key == 'INVALID_POSTCODE'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "search_for_invalid_opening_times" {
  name = "${var.project_id}/${var.blue_green_environment}/search-for-invalid-opening-times"

  log_group_names = [
    "/aws/lambda/${var.service_sync_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter report_key == 'INVALID_OPEN_TIMES'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "search_by_email_correlation_id" {
  name = "${var.project_id}/${var.blue_green_environment}/search-by-email-correlation-id"

  log_group_names = [
    "/aws/lambda/${var.service_sync_lambda_name}",
    "/aws/lambda/${var.send_email_lambda_name}"
  ]

  query_string = <<EOF
fields correlation_id
| filter message =="Email Correlation Id"
| filter email_correlation_id == "ADD_EMAIL_CORRELATION_ID"
EOF
}
