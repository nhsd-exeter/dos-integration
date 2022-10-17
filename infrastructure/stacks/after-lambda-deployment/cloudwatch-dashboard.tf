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
            "width": 4,
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
            "type": "metric",
            "x": 16,
            "y": 0,
            "width": 8,
            "height": 6,
            "properties": {
                "sparkline": true,
                "view": "singleValue",
                "metrics": [
                    [ "UEC-DOS-INT", "UpdateRequestFailed", "ENV", "${var.environment}" ],
                    [ "UEC-DOS-INT", "UpdateRequestSuccess", "ENV", "${var.environment}" ],
                    [ "UEC-DOS-INT", "ServiceSyncHealthCheckSuccess", "ENV", "${var.environment}" ],
                    [ "UEC-DOS-INT", "ServiceSyncHealthCheckFailure", "ENV", "${var.environment}" ]
                ],
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 3600,
                "stat": "Sum",
                "title": "Service Sync Responses in the last hour"
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
                    [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", "${var.change_event_queue_name}" ],
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
            "type": "metric",
            "x": 9,
            "y": 6,
            "width": 9,
            "height": 6,
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", "${var.update_request_queue_name}" ],
                    [ ".", "NumberOfMessagesReceived", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesVisible", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesNotVisible", ".", "." ]
                ],
                "stat": "Sum",
                "period": 60,
                "region": "${var.aws_region}",
                "title": "Update Request Queue"
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
                    [ "AWS/SQS", "NumberOfMessagesReceived", "QueueName", "${var.update_request_dlq}", { "label": "UR DLQ Message Count" } ],
                    [ "AWS/SQS", "NumberOfMessagesReceived", "QueueName", "${var.change_event_dlq}", { "label": "CE DLQ Message Count" } ]
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
            "height": 6,
            "width": 4,
            "y": 12,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.dos_db_name}", { "stat": "Maximum" } ],
                    [ "AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.dos_db_replica_name}", { "stat": "Maximum" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 60,
                "stat": "Minimum",
                "title": "DB Connections"
            }
        },
        {
            "height": 6,
            "width": 4,
            "y": 12,
            "x": 4,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.dos_db_name}" ],
                    [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.dos_db_replica_name}" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 60,
                "stat": "Maximum",
                "title": "DB CPU Utilization"
            }
        },
        {
            "height": 6,
            "width": 4,
            "y": 12,
            "x": 8,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "AWS/RDS", "ReplicaLag", "DBInstanceIdentifier", "uec-core-dos-regression-db-12-replica-di" ]
                ],
                "region": "eu-west-2"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 12,
            "x": 12,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "AWS/Lambda", "ConcurrentExecutions", "FunctionName", "${var.service_matcher_lambda_name}" ],
                    [ ".", "Duration", ".", "." ],
                    [ ".", "Errors", ".", ".", { "visible": false } ],
                    [ "...", { "id": "errors", "stat": "Sum", "color": "#d62728" } ],
                    [ ".", "Invocations", ".", ".", { "id": "invocations", "stat": "Sum" } ],
                    [ { "expression": "100 - 100 * errors / MAX([errors, invocations])", "label": "Success rate (%)", "id": "availability", "yAxis": "right", "region": "${var.aws_region}", "color": "#2ca02c" } ]
                ],
                "region": "${var.aws_region}",
                "title": "Service Matcher",
                "period": 60
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
                    [ "AWS/Lambda", "ConcurrentExecutions", "FunctionName", "${var.service_sync_lambda_name}" ],
                    [ ".", "Duration", ".", "." ],
                    [ ".", "Errors", ".", ".", { "visible": false } ],
                    [ "...", { "id": "errors", "stat": "Sum", "color": "#d62728" } ],
                    [ ".", "Invocations", ".", ".", { "id": "invocations", "stat": "Sum" } ],
                    [ { "expression": "100 - 100 * errors / MAX([errors, invocations])", "label": "Success rate (%)", "id": "availability", "yAxis": "right", "region": "${var.aws_region}", "color": "#2ca02c" } ]
                ],
                "region": "${var.aws_region}",
                "title": "Service Sync",
                "period": 60
            }
        }
    ]
}
EOF
}
