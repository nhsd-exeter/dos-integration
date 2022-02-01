resource "aws_cloudwatch_dashboard" "cloudwatch_dashboard" {

  dashboard_name = var.cloudwatch_performance_dashboard_name
  dashboard_body = <<EOF
{
    "widgets": [
        {
            "height": 6,
            "width": 23,
            "y": 0,
            "x": 0,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "UEC-DOS-INT", "ProcessingLatency", "ServiceName", "${var.project_id}-perf-event-sender", "LogGroup", "${var.project_id}-${var.environment}-event-sender", "ServiceType", "AWS::Lambda::Function", "ENV", "${var.environment}" ]
                ],
                "region": "${var.aws_region}"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 16,
            "x": 6,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "UEC-DOS-INT", "DosApiLatency", "ServiceName", "${var.project_id}-perf-event-sender", "LogGroup", "${var.project_id}-${var.environment}-event-sender", "ServiceType", "AWS::Lambda::Function", "ENV", "${var.environment}" ]
                ],
                "region": "${var.aws_region}"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 10,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "ConcurrentExecutions", "FunctionName", "${var.project_id}-${var.environment}-perf-event-processor" ],
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
                "period": 300,
                "stat": "Average"
            }
        },
        {
            "height": 4,
            "width": 23,
            "y": 6,
            "x": 0,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", "${var.project_id}-${var.environment}-perf-fifo-queue.fifo" ],
                    [ ".", "NumberOfMessagesReceived", ".", "." ],
                    [ ".", "ApproximateAgeOfOldestMessage", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesVisible", ".", "." ],
                    [ ".", "ApproximateNumberOfMessagesNotVisible", ".", "." ]
                ],
                "region": "${var.aws_region}",
                "title": "SQS"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 10,
            "x": 6,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.project_id}-${var.environment}-perf-${var.dos_db_name}", { "stat": "Maximum" } ],
                    [ "..." ],
                    [ "...", { "stat": "Average" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 300,
                "stat": "Minimum",
                "title": "Max DB Connections"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 10,
            "x": 12,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.project_id}-${var.environment}-perf-${var.dos_db_name}" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "${var.aws_region}",
                "period": 300,
                "stat": "Maximum"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 16,
            "x": 0,
            "type": "metric",
            "properties": {
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "AWS/Lambda", "ConcurrentExecutions", "FunctionName", "${var.project_id}-${var.environment}-perf-event-sender" ],
                    [ ".", "Duration", ".", "." ],
                    [ ".", "Errors", ".", "." ]
                ],
                "region": "${var.aws_region}",
                "title": "Event Sender",
                "period": 300
            }
        }
    ]
}
EOF

  tags = {
    service = var.project_id
  }
}
