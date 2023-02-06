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
              [".", ".", ".", var.blue_green_environment, { "stat" : "Maximum", "id" : "m2", "visible" : false }]
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
              [".", "UpdateRequestSuccess", ".", var.blue_green_environment],
              [".", "ServiceSyncHealthCheckSuccess", ".", var.blue_green_environment],
              [".", "ServiceSyncHealthCheckFailure", ".", var.blue_green_environment],
              [".", "ChangeEventReceived", ".", var.blue_green_environment]
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
              [".", "5XXError", ".", var.di_endpoint_api_gateway_name]
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
              [".", ".", ".", var.holding_queue_dlq, { "label" : "Holding Queue DLQ Message Count" }],
              [".", ".", ".", var.change_event_dlq, { "label" : "Change Event DLQ Message Count" }]
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
          width : 6,
          y : 12,
          x : 0,
          type : "metric",
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.ingest_change_event_lambda_name],
              [".", "Duration", ".", "."],
              [".", "Errors", ".", ".", { "visible" : false }],
              ["...", { "id" : "errors", stat : "Sum", "color" : "#d62728" }],
              [".", "Invocations", ".", ".", { "id" : "invocations", stat : "Sum" }],
              [{ "expression" : "100 - 100 * errors / MAX([errors, invocations])", "label" : "Success rate (%)", "id" : "availability", "yAxis" : "right", "region" : var.aws_region, "color" : "#2ca02c" }]
            ],
            region : var.aws_region,
            title : "Ingest Change Event Lambda",
            period : 60
          }
        },
        {
          height : 6,
          width : 6,
          y : 12,
          x : 6,
          type : "metric",
          properties : {
            view : "timeSeries",
            stacked : false,
            metrics : [
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.service_matcher_lambda_name],
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
          x : 12,
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
              ["AWS/Lambda", "Errors", "FunctionName", var.change_event_dlq_handler_lambda_name, { "id" : "m11", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.change_event_dlq_handler_lambda_name, { "id" : "m12", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m11/m12) * 100", "label" : "Change Event DLQ Handler", region : var.aws_region }],
              ["AWS/Lambda", "Errors", "FunctionName", var.dos_db_update_dlq_handler_lambda_name, { "id" : "m21", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.dos_db_update_dlq_handler_lambda_name, { "id" : "m22", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m21/m22) * 100", "label" : "DoS DB Update Handler", region : var.aws_region }],
              ["AWS/Lambda", "Errors", "FunctionName", var.event_replay_lambda_name, { "id" : "m31", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.event_replay_lambda_name, { "id" : "m32", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m31/m32) * 100", "label" : "Event Replay", region : var.aws_region }],
              ["AWS/Lambda", "Errors", "FunctionName", var.ingest_change_event_lambda_name, { "id" : "m41", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.ingest_change_event_lambda_name, { "id" : "m42", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m41/m42) * 100", "label" : "Ingest Change Event", region : var.aws_region }],
              ["AWS/Lambda", "Errors", "FunctionName", var.send_email_lambda_name, { "id" : "m51", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.send_email_lambda_name, { "id" : "m52", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m51/m52) * 100", "label" : "Send Email", region : var.aws_region }],
              ["AWS/Lambda", "Errors", "FunctionName", var.service_matcher_lambda_name, { "id" : "m61", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.service_matcher_lambda_name, { "id" : "m62", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m61/m62) * 100", "label" : "Service Matcher", region : var.aws_region }],
              ["AWS/Lambda", "Errors", "FunctionName", var.service_sync_lambda_name, { "id" : "m71", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.service_sync_lambda_name, { "id" : "m72", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m71/m72) * 100", "label" : "Service Sync", region : var.aws_region }],
              ["AWS/Lambda", "Errors", "FunctionName", var.slack_messenger_lambda_name, { "id" : "m81", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.slack_messenger_lambda_name, { "id" : "m82", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m81/m82) * 100", "label" : "Slack Messenger", region : var.aws_region }]
            ],
            region : var.aws_region,
            title : "Lambda Error Rates (%) -> Above 0 is bad",
            period : 60
            yAxis : {
              left : {
                label : "Percentage",
                showUnits : false
            } }
          }
        },
        {
          height : 6,
          width : 4,
          y : 18,
          x : 0,
          type : "metric",
          properties : {
            metrics : [
              ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.dos_db_name, { stat : "Maximum" }],
              [".", ".", ".", var.dos_db_replica_name, { stat : "Maximum" }]
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
          y : 18,
          x : 4,
          type : "metric",
          properties : {
            metrics : [
              ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.dos_db_name],
              [".", ".", ".", var.dos_db_replica_name]
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
          y : 18,
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
      ]
    }
  )
}
