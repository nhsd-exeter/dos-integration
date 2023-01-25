resource "aws_cloudwatch_dashboard" "cloudwatch_dashboard" {
  dashboard_name = var.cloudwatch_monitoring_dashboard_name
  dashboard_body = jsonencode(
    {
      widgets : [
        {
          type : "text",
          x : 0,
          y : 0,
          width : 3,
          height : 6,
          properties : {
            "markdown" : "Shared Environment\n- **${var.shared_environment}**\n\nCurrent Blue/Green Version\n\n- **${var.blue_green_environment}**\n\nPrevious Blue/Green Version\n\n- **${var.previous_blue_green_environment}**"
          }
        },
        {
          height : 6,
          width : 11,
          y : 0,
          x : 3,
          type : "metric",
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              [{ "expression" : "m1/60000", "label" : "QueueToDoSLatency Average in Minutes", "id" : "e1" }],
              [{ "expression" : "m2/60000", "label" : "QueueToDoSLatency Maximum in Minutes", "id" : "e2" }],
              ["UEC-DOS-INT", "QueueToDoSLatency", "ENV", var.blue_green_environment, { "id" : "m1", "visible" : false }],
              ["UEC-DOS-INT", "QueueToDoSLatency", "ENV", var.blue_green_environment, { "stat" : "Maximum", "id" : "m2", "visible" : false }]
            ],
            period : 60,
            region : var.aws_region,
            title : "System Latency"
          }
        },
        {
          type : "metric",
          x : 14,
          y : 0,
          width : 10,
          height : 6,
          properties : {
            "sparkline" : true,
            view : "singleValue",
            metrics : [
              ["UEC-DOS-INT", "UpdateRequestFailed", "ENV", var.blue_green_environment],
              ["UEC-DOS-INT", "UpdateRequestSuccess", "ENV", var.blue_green_environment],
              ["UEC-DOS-INT", "ServiceSyncHealthCheckSuccess", "ENV", var.blue_green_environment],
              ["UEC-DOS-INT", "ServiceSyncHealthCheckFailure", "ENV", var.blue_green_environment],
              ["UEC-DOS-INT", "ChangeEventReceived", "ENV", var.blue_green_environment]
            ],
            stacked : false,
            region : var.aws_region,
            period : 3600,
            stat : "Sum",
            title : "Custom Metrics in the last hour"
          }
        },
        {
          height : 6,
          width : 7,
          y : 6,
          x : 0,
          type : "metric",
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.change_event_queue_name],
              [".", "NumberOfMessagesReceived", ".", "."]
            ],
            stat : "Sum",
            period : 60,
            region : var.aws_region,
            title : "Change Event Queue"
          }
        },
        {
          type : "metric",
          x : 7,
          y : 6,
          width : 7,
          height : 6,
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.update_request_queue_name],
              [".", "NumberOfMessagesReceived", ".", "."]
            ],
            stat : "Sum",
            period : 60,
            region : var.aws_region,
            title : "Update Request Queue"
          }
        },
        {
          height : 6,
          width : 4,
          y : 6,
          x : 14,
          type : "metric",
          properties : {
            metrics : [
              ["AWS/ApiGateway", "4XXError", "ApiName", var.di_endpoint_api_gateway_name],
              ["AWS/ApiGateway", "5XXError", "ApiName", var.di_endpoint_api_gateway_name]
            ],
            view : "timeSeries",
            stacked : false,
            region : var.aws_region,
            stat : "Sum",
            period : 60,
            title : "NHS UK Endpoint Errors"
          }
        },
        {
          type : "metric",
          x : 18,
          y : 6,
          width : 6,
          height : 6,
          properties : {
            metrics : [
              ["AWS/SQS", "NumberOfMessagesReceived", "QueueName", var.update_request_dlq, { "label" : "Update Request DLQ Message Count" }],
              ["AWS/SQS", "NumberOfMessagesReceived", "QueueName", var.holding_queue_dlq, { "label" : "Holding Queue DLQ Message Count" }],
              ["AWS/SQS", "NumberOfMessagesReceived", "QueueName", var.change_event_dlq, { "label" : "Change Event DLQ Message Count" }]
            ],
            view : "timeSeries",
            stacked : false,
            region : var.aws_region,
            stat : "Sum",
            period : 60,
            title : "Dead Letter Queue messages"
          }
        },
        {
          height : 6,
          width : 4,
          y : 12,
          x : 0,
          type : "metric",
          properties : {
            metrics : [
              ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.dos_db_name, { stat : "Maximum" }],
              ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.dos_db_replica_name, { stat : "Maximum" }]
            ],
            view : "timeSeries",
            stacked : false,
            region : var.aws_region,
            period : 60,
            stat : "Minimum",
            title : "DB Connections"
          }
        },
        {
          height : 6,
          width : 4,
          y : 12,
          x : 4,
          type : "metric",
          properties : {
            metrics : [
              ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.dos_db_name],
              ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.dos_db_replica_name]
            ],
            view : "timeSeries",
            stacked : false,
            region : var.aws_region,
            period : 60,
            stat : "Maximum",
            title : "DB CPU Utilization"
          }
        },
        {
          height : 6,
          width : 4,
          y : 12,
          x : 8,
          type : "metric",
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              ["AWS/RDS", "ReplicaLag", "DBInstanceIdentifier", var.dos_db_replica_name]
            ],
            region : var.aws_region
          }
        },
        {
          height : 6,
          width : 6,
          y : 12,
          x : 12,
          type : "metric",
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", "${var.service_matcher_lambda_name}"],
              [".", "Duration", ".", "."],
              [".", "Errors", ".", ".", { "visible" : false }],
              ["...", { "id" : "errors", stat : "Sum", "color" : "#d62728" }],
              [".", "Invocations", ".", ".", { "id" : "invocations", stat : "Sum" }],
              [{ "expression" : "100 - 100 * errors / MAX([errors, invocations])", "label" : "Success rate (%)", "id" : "availability", "yAxis" : "right", "region" : var.aws_region, "color" : "#2ca02c" }]
            ],
            region : var.aws_region,
            title : "Service Matcher",
            period : 60
          }
        },
        {
          height : 6,
          width : 6,
          y : 12,
          x : 18,
          type : "metric",
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.service_sync_lambda_name],
              [".", "Duration", ".", "."],
              [".", "Errors", ".", ".", { "visible" : false }],
              ["...", { "id" : "errors", stat : "Sum", "color" : "#d62728" }],
              [".", "Invocations", ".", ".", { "id" : "invocations", stat : "Sum" }],
              [{ "expression" : "100 - 100 * errors / MAX([errors, invocations])", "label" : "Success rate (%)", "id" : "availability", "yAxis" : "right", region : var.aws_region, "color" : "#2ca02c" }]
            ],
            region : var.aws_region,
            title : "Service Sync",
            period : 60
          }
        }
      ]
    }
  )
}
