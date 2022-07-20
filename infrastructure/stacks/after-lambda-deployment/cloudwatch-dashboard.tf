resource "aws_cloudwatch_dashboard" "cloudwatch_dashboard" {
  dashboard_name = var.cloudwatch_monitoring_dashboard_name
  dashboard_body = <<EOF
{
    "widgets": [
        {
            "height": 6,
            "width": 12,
            "y": 0,
            "x": 0,
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
            "x": 12,
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
            "y": 12,
            "x": 18,
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
                "title": "Change Event Queue"
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
                "title": "DI DB Replica Connections"
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
                "stat": "Maximum",
                "title": "DI DB Replica CPU Utilization"
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
                    [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", "${var.cr_fifo_queue_name}", { "label": "Change Request", "region": "${var.aws_region}" } ]
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
                "title": "Change Request Queue"
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
                    [ "AWS/SQS", "NumberOfMessagesReceived", "QueueName", "${var.cr_dead_letter_queue_from_fifo_queue_name}", { "label": "CR FIFO Message Count" } ],
                    [ "...", "${var.dead_letter_queue_from_fifo_queue_name}", { "label": "CE FIFO Message Count" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "stat": "Sum",
                "period": 60,
                "title": "Dead Letter Queue messages"
            }
        },
        {
            "type": "metric",
            "x": 18,
            "y": 6,
            "width": 6,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "UEC-DOS-INT", "DoSApiFail", "ENV", "${var.environment}" ],
                    [ "UEC-DOS-INT", "DoSApiUnavailable", "ENV", "${var.environment}" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 60,
                "stat": "Sum",
                "title": "DoS API failures / unavailable"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 18,
            "width": 6,
            "height": 6,
            "properties": {
              "sparkline": true,
              "period": 60,
              "metrics": [
                  [ "AWS/Lambda", "Errors", "FunctionName", "uec-dos-int-${var.environment}-event-processor", { "id": "errors", "stat": "Sum", "color": "#d13212" } ],
                  [ ".", "Invocations", ".", ".", { "id": "invocations", "stat": "Sum", "visible": false } ],
                  [ { "expression": "100 - 100 * errors / MAX([errors, invocations])", "label": "Success rate (%)", "id": "availability", "yAxis": "right", "region": "${var.aws_region}" } ]
              ],
              "region": "${var.aws_region}",
              "title": "Event Processor Error count and success rate (%)",
              "yAxis": {
                  "right": {
                      "max": 100
                  }
              },
              "view": "timeSeries",
              "stacked": true,
              "setPeriodToTimeRange": true
              }
        },
        {
            "type": "metric",
            "x": 18,
            "y": 18,
            "width": 6,
            "height": 6,
            "properties": {
              "sparkline": true,
              "period": 60,
              "metrics": [
                  [ "AWS/Lambda", "Errors", "FunctionName", "uec-dos-int-${var.environment}-event-sender", { "id": "errors", "stat": "Sum", "color": "#d13212" } ],
                  [ ".", "Invocations", ".", ".", { "id": "invocations", "stat": "Sum", "visible": false } ],
                  [ { "expression": "100 - 100 * errors / MAX([errors, invocations])", "label": "Success rate (%)", "id": "availability", "yAxis": "right", "region": "${var.aws_region}" } ]
              ],
              "region": "${var.aws_region}",
              "title": "Event Sender Error count and success rate (%)",
              "yAxis": {
                  "right": {
                      "max": 100
                  }
              },
              "view": "timeSeries",
              "stacked": true,
              "setPeriodToTimeRange": true
              }
        }
    ]
}
EOF
}
