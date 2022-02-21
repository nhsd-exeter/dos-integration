resource "aws_cloudwatch_query_definition" "errors" {
  name = "${var.project_id}/${var.environment}/errors"

  log_group_names = [
    "/aws/lambda/${var.event_processor_lambda_name}",
    "/aws/lambda/${var.event_sender_lambda_name}",
    "/aws/lambda/${var.eventbridge_dlq_handler_lambda_name}",
    "/aws/lambda/${var.fifo_dlq_handler_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message, exception_name
| filter level == 'ERROR'
| sort @timestamp
EOF
}

resource "aws_cloudwatch_query_definition" "by_correlation_id" {
  name = "${var.project_id}/${var.environment}/by-correlation-id"

  log_group_names = [
    "/aws/lambda/${var.event_processor_lambda_name}",
    "/aws/lambda/${var.event_sender_lambda_name}",
    "/aws/lambda/${var.eventbridge_dlq_handler_lambda_name}",
    "/aws/lambda/${var.fifo_dlq_handler_lambda_name}",
    "/aws/lambda/${var.event_replay_lambda_name}"
  ]

  query_string = <<EOF
fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message
| filter correlation_id == 'REPLACE'
| sort @timestamp
EOF
}



resource "aws_cloudwatch_dashboard" "cloudwatch_dashboard" {

  dashboard_name = var.cloudwatch_monitoring_dashboard_name
  dashboard_body = <<EOF
{
    "widgets": [
        {
            "height": 6,
            "width": 12,
            "y": 0,
            "x": 6,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "UEC-DOS-INT", "QueueToProcessorLatency", "ENV", "${var.environment}" ],
                    [ "UEC-DOS-INT", "QueueToDoSLatency", "ENV", "${var.environment}" ],
                    [ "...", { "stat": "TM(0%:90%)" } ]
                ],
                "period": 60,
                "region": "${var.aws_region}",
                "title": "System Latency"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 0,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/ApiGateway", "4XXError", "ApiName", "${var.di_endpoint_api_gateway_name}" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "stat": "Sum",
                "period": 60,
                "title": "NHS UK Endpoint 4xxError"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 18,
            "x": 12,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "UEC-DOS-INT", "DosApiLatency","ENV", "${var.environment}" ]
                ],
                "period": 60,
                "region": "${var.aws_region}"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 18,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "ConcurrentExecutions", "FunctionName", "${var.event_processor_lambda_name}" ],
                    [ ".", "Errors", ".", ".", { "stat": "Sum" } ],
                    [ ".", "Invocations", ".", "." ],
                    [ ".", "Duration", ".", "." ],
                    [ ".", "Throttles", ".", ".", { "stat": "Sum" } ],
                    [ ".", "Duration", ".", ".", { "stat": "Minimum" } ],
                    [ "...", { "stat": "Maximum" } ],
                    [ "...", { "stat": "TM(10%:90%)" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "title": "Event Processor",
                "period": 60,
                "stat": "Average"
            }
        },
        {
            "height": 6,
            "width": 9,
            "y": 6,
            "x": 0,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,

                "metrics": [
                    [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", "${var.fifo_queue_name}" ],
                    [ ".", "NumberOfMessagesReceived", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesVisible", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesNotVisible", ".", "." ]
                ],
                "stat": "Sum",
                "period": 60,
                "region": "${var.aws_region}",
                "title": "CE Queue"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 12,
            "x": 6,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.dos_db_name}", { "stat": "Maximum" } ],
                    [ "..." ],
                    [ "...", { "stat": "Average" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 60,
                "stat": "Minimum",
                "title": "Max DB Connections"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 12,
            "x": 12,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.dos_db_name}" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 60,
                "stat": "Maximum"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 18,
            "x": 6,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "AWS/Lambda", "ConcurrentExecutions", "FunctionName", "${var.event_sender_lambda_name}" ],
                    [ ".", "Duration", ".", "." ],
                    [ ".", "Errors", ".", "." ]
                ],
                "region": "${var.aws_region}",
                "title": "Event Sender",
                "period": 60
            }
        },
        {
            "type": "metric",
            "height": 6,
            "width": 6,
            "y": 12,
            "x": 0,
            "properties": {
                "metrics": [
                    [ "AWS/ApiGateway", "Count", "ApiName", "${var.di_endpoint_api_gateway_name}", { "label": "NHSUK Change Event", "region": "${var.aws_region}" } ],
                    [ "AWS/Lambda", "Invocations", "FunctionName", "${var.event_sender_lambda_name}", { "label": "Change Request", "region": "${var.aws_region}" } ]

                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 60,
                "stat": "Sum",
                "title": "Message Count"
            }
        },
        {
            "type": "metric",
            "x": 9,
            "y": 6,
            "width": 9,
            "height": 6,
            "properties": {
                "view": "timeSeries",
                "stacked": false,

                "metrics": [
                    [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", "${var.cr_fifo_queue_name}" ],
                    [ ".", "NumberOfMessagesReceived", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesVisible", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesNotVisible", ".", "." ]
                ],
                "stat": "Sum",
                "period": 60,
                "region": "${var.aws_region}",
                "title": "CR Queue"
            }
        },
        {
            "type": "metric",
            "x": 18,
            "y": 0,
            "width": 6,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/SQS", "NumberOfMessagesReceived", "QueueName", "${var.dead_letter_queue_from_event_bus_name}", { "label": "EventBridge Message Count" } ],
                    [ "...", "${var.dead_letter_queue_from_fifo_queue_name}", { "label": "FIFO Message Count" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "stat": "Sum",
                "period": 60,
                "title": "DLQ failures"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 24,
            "width": 6,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "UEC-DOS-INT", "DoSApiFail", "ENV", "${var.environment}" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 300,
                "stat": "Sum"
            }
        }
    ]
}
EOF
}
