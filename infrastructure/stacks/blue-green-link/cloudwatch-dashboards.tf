resource "aws_cloudwatch_dashboard" "cloudwatch_monitoring_dashboard" {
  dashboard_name = var.cloudwatch_monitoring_dashboard_name
  dashboard_body = jsonencode(
    {
      "widgets" : [
        {
          "type" : "text",
          "x" : 0,
          "y" : 0,
          "width" : 3,
          "height" : 6,
          "properties" : {
            "markdown" : "Shared Environment\n- **${var.shared_environment}**\n\nCurrent Blue/Green Version\n\n- **${var.blue_green_environment}**\n\nPrevious Blue/Green Version\n\n- **${var.previous_blue_green_environment}**"
          }
        },
        {
          "height" : 6,
          "width" : 13,
          "y" : 0,
          "x" : 3,
          "type" : "metric",
          "properties" : {
            "view" : "gauge",
            "metrics" : [
              ["UEC-DOS-INT", "QueueToDoSLatency", "ENV", "test", { "region" : "eu-west-2" }]
            ],
            "yAxis" : {
              "left" : {
                "min" : 0,
                "max" : 300000
              }
            },
            "region" : var.aws_region,
            "period" : 300,
            "annotations" : {
              "horizontal" : [
                {
                  "color" : "#2ca02c",
                  "label" : "Below SLA",
                  "value" : 120000,
                  "fill" : "below"
                },
                {
                  "color" : "#d62728",
                  "label" : "Above SLA",
                  "value" : 120000,
                  "fill" : "above"
                }
              ]
            },
            "setPeriodToTimeRange" : true,
            "title" : "Message Latency Last 5 Minutes"
          }
        },
        {
          "type" : "metric",
          "x" : 16,
          "y" : 0,
          "width" : 8,
          "height" : 6,
          "properties" : {
            "sparkline" : true,
            "view" : "singleValue",
            "metrics" : [
              ["UEC-DOS-INT", "UpdateRequestSuccess", "ENV", var.blue_green_environment, { "region" : var.aws_region, "color" : "#2ca02c", "label" : "DoS Service Update Success" }],
              [".", "UpdateRequestFailed", ".", var.blue_green_environment, { "region" : var.aws_region, "color" : "#d62728", "label" : "DoS Service Update Failed" }],
              [".", "ChangeEventReceived", ".", var.blue_green_environment, { "region" : var.aws_region, "color" : "#1f77b4", "label" : "Change Event Received" }],
              [".", "DoSAllServiceUpdates", ".", var.blue_green_environment, { "label" : "All DoS Data Item Updates", "color" : "#000000" }],
            ],
            "stacked" : false,
            "region" : var.aws_region,
            "period" : 3600,
            "stat" : "Sum",
            "title" : "System Health (Per Hour)",
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 13,
          "y" : 6,
          "x" : 0,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              [{ "expression" : "m1/60000", "label" : "QueueToDoSLatency Average", "id" : "e1" }],
              [{ "expression" : "m2/60000", "label" : "QueueToDoSLatency Maximum", "id" : "e2" }],
              ["UEC-DOS-INT", "QueueToDoSLatency", "ENV", var.blue_green_environment, { "id" : "m1", "visible" : false }],
              [".", ".", ".", var.blue_green_environment, { "stat" : "Maximum", "id" : "m2", "visible" : false }]
            ],
            "period" : 60,
            "region" : var.aws_region,
            "title" : "System Latency"
            "yAxis" : {
              "left" : {
                "label" : "Minutes",
                "showUnits" : false
            } },
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 5,
          "y" : 6,
          "x" : 13,
          "type" : "metric",
          "properties" : {
            "metrics" : [
              ["AWS/ApiGateway", "Count", "ApiName", "uec-dos-int-ds-1328-di-endpoint", "Stage", "ds-1328"]
            ],
            "period" : 60,
            "stat" : "Sum",
            "region" : "eu-west-2",
            "view" : "timeSeries",
            "stacked" : false,
            "title" : "DI Endpoint Requests"
            "yAxis" : {
              "left" : {
                "showUnits" : true
              }
            },
            "legend" : {
              "position" : "hidden"
            }
          }
        },
        {
          "height" : 6,
          "width" : 6,
          "y" : 6,
          "x" : 18,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/Lambda", "Errors", "FunctionName", var.change_event_dlq_handler_lambda_name, { "id" : "m11", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.change_event_dlq_handler_lambda_name, { "id" : "m12", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m11/m12) * 100", "label" : "Change Event DLQ Handler", region : var.aws_region, "color" : "#1f77b4" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.dos_db_update_dlq_handler_lambda_name, { "id" : "m21", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.dos_db_update_dlq_handler_lambda_name, { "id" : "m22", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m21/m22) * 100", "label" : "DoS DB Update Handler", region : var.aws_region, "color" : "#ff7f0e" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.event_replay_lambda_name, { "id" : "m31", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.event_replay_lambda_name, { "id" : "m32", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m31/m32) * 100", "label" : "Event Replay", region : var.aws_region, "color" : "#2ca02c" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.ingest_change_event_lambda_name, { "id" : "m41", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.ingest_change_event_lambda_name, { "id" : "m42", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m41/m42) * 100", "label" : "Ingest Change Event", region : var.aws_region, "color" : "#d62728" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.send_email_lambda_name, { "id" : "m51", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.send_email_lambda_name, { "id" : "m52", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m51/m52) * 100", "label" : "Send Email", region : var.aws_region, "color" : "#9467bd" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.service_matcher_lambda_name, { "id" : "m61", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.service_matcher_lambda_name, { "id" : "m62", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m61/m62) * 100", "label" : "Service Matcher", region : var.aws_region, "color" : "#8c564b" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.service_sync_lambda_name, { "id" : "m71", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.service_sync_lambda_name, { "id" : "m72", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m71/m72) * 100", "label" : "Service Sync", region : var.aws_region, "color" : "#e377c2" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.slack_messenger_lambda_name, { "id" : "m81", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.slack_messenger_lambda_name, { "id" : "m82", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m81/m82) * 100", "label" : "Slack Messenger", region : var.aws_region, "color" : "#bcbd22" }]
            ],
            "region" : var.aws_region,
            "title" : "Lambda Error Rates (%) -> Above 0 is bad",
            "period" : 60
            "yAxis" : {
              "left" : {
                "label" : "Percentage",
                "showUnits" : false
            } },
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 6,
          "y" : 12,
          "x" : 0,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.ingest_change_event_lambda_name],
              [".", "Duration", ".", "."],
              [".", "Errors", ".", ".", { "visible" : false }],
              ["...", { "id" : "errors", stat : "Sum", "color" : "#d62728" }],
              [".", "Invocations", ".", ".", { "id" : "invocations", stat : "Sum" }],
              [{ "expression" : "100 - 100 * errors / MAX([errors, invocations])", "label" : "Success rate (%)", "id" : "availability", "yAxis" : "right", "region" : var.aws_region, "color" : "#2ca02c" }]
            ],
            "region" : var.aws_region,
            "title" : "Ingest Change Event Lambda",
            "period" : 60,
            "timezone" : "LOCAL"
            "yAxis" : {
              "right" : {
                "showUnits" : false
              }
            }
          }
        },
        {
          "height" : 6,
          "width" : 6,
          "y" : 12,
          "x" : 6,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.service_matcher_lambda_name],
              [".", "Duration", ".", "."],
              [".", "Errors", ".", ".", { "visible" : false }],
              ["...", { "id" : "errors", stat : "Sum", "color" : "#d62728" }],
              [".", "Invocations", ".", ".", { "id" : "invocations", stat : "Sum" }],
              [{ "expression" : "100 - 100 * errors / MAX([errors, invocations])", "label" : "Success rate (%)", "id" : "availability", "yAxis" : "right", "region" : var.aws_region, "color" : "#2ca02c" }]
            ],
            "region" : var.aws_region,
            "title" : "Service Matcher",
            "period" : 60,
            "timezone" : "LOCAL"
            "yAxis" : {
              "right" : {
                "showUnits" : false
              }
            }
          }
        },
        {
          "height" : 6,
          "width" : 6,
          "y" : 12,
          "x" : 12,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.service_sync_lambda_name],
              [".", "Duration", ".", "."],
              [".", "Errors", ".", ".", { "visible" : false }],
              ["...", { "id" : "errors", stat : "Sum", "color" : "#d62728" }],
              [".", "Invocations", ".", ".", { "id" : "invocations", stat : "Sum" }],
              [{ "expression" : "100 - 100 * errors / MAX([errors, invocations])", "label" : "Success rate (%)", "id" : "availability", "yAxis" : "right", region : var.aws_region, "color" : "#2ca02c" }]
            ],
            "region" : var.aws_region,
            "title" : "Service Sync",
            "period" : 60,
            "timezone" : "LOCAL"
            "yAxis" : {
              "right" : {
                "showUnits" : false
              }
            }
          }
        },
        {
          "height" : 6,
          "width" : 6,
          "y" : 12,
          "x" : 18,
          "type" : "metric",
          "properties" : {
            "metrics" : [
              ["AWS/SQS", "NumberOfMessagesReceived", "QueueName", var.update_request_dlq, { "label" : "Update Request DLQ" }],
              [".", ".", ".", var.holding_queue_dlq, { "label" : "Holding Queue DLQ" }],
              [".", ".", ".", var.change_event_dlq, { "label" : "Change Event DLQ" }]
            ],
            "view" : "timeSeries",
            "stacked" : false,
            "region" : var.aws_region,
            "stat" : "Sum",
            "period" : 60,
            "title" : "Dead Letter Queue messages",
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 8,
          "y" : 18,
          "x" : 0,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.change_event_queue_name],
              [".", "NumberOfMessagesReceived", ".", "."],
              [".", "ApproximateNumberOfMessagesVisible", ".", "."]
            ],
            "stat" : "Sum",
            "period" : 60,
            "region" : var.aws_region,
            "title" : "Change Event Queue",
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 8,
          "y" : 18,
          "x" : 8,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.holding_queue_name],
              [".", "NumberOfMessagesReceived", ".", "."],
              [".", "ApproximateNumberOfMessagesVisible", ".", "."],
            ],
            "stat" : "Sum",
            "period" : 60,
            "region" : var.aws_region,
            "title" : "Holding Queue",
            "timezone" : "LOCAL"
          }
        },
        {
          "type" : "metric",
          "height" : 6,
          "width" : 8,
          "y" : 18,
          "x" : 16,
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.update_request_queue_name],
              [".", "NumberOfMessagesReceived", ".", "."],
              [".", "ApproximateNumberOfMessagesVisible", ".", "."],
            ],
            "stat" : "Sum",
            "period" : 60,
            "region" : var.aws_region,
            "title" : "Update Request Queue",
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 4,
          "y" : 24,
          "x" : 0,
          "type" : "metric",
          "properties" : {
            "metrics" : [
              ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.dos_db_name, { stat : "Maximum" }],
              ["...", var.dos_db_replica_name, { stat : "Maximum" }]
            ],
            "view" : "timeSeries",
            "stacked" : false,
            "region" : var.aws_region,
            "period" : 60,
            "stat" : "Minimum",
            "title" : "DB Connections",
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 4,
          "y" : 24,
          "x" : 4,
          "type" : "metric",
          "properties" : {
            "metrics" : [
              ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.dos_db_name],
              ["...", var.dos_db_replica_name]
            ],
            "view" : "timeSeries",
            "stacked" : false,
            "region" : var.aws_region,
            "period" : 60,
            "stat" : "Maximum",
            "title" : "DB CPU Utilization",
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 4,
          "y" : 24,
          "x" : 8,
          "type" : "metric",
          "properties" : {
            "view" : "timeSeries",
            "stacked" : false,
            "metrics" : [
              ["AWS/RDS", "AuroraReplicaLag", "DBClusterIdentifier", var.dos_db_replica_name]
            ],
            "region" : var.aws_region,
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 6,
          "y" : 24,
          "x" : 12,
          "type" : "metric",
          "properties" : {
            "metrics" : [
              ["AWS/ApiGateway", "4XXError", "ApiName", var.di_endpoint_api_gateway_name],
              [".", "5XXError", ".", var.di_endpoint_api_gateway_name]
            ],
            "view" : "timeSeries",
            "stacked" : false,
            "region" : var.aws_region,
            "stat" : "Sum",
            "period" : 60,
            "title" : "DI Endpoint Errors",
            "timezone" : "LOCAL"
          }
        }
      ]
    }
  )
}

resource "aws_cloudwatch_dashboard" "cloudwatch_data_dashboard" {
  dashboard_name = var.cloudwatch_data_dashboard_name
  dashboard_body = jsonencode({
    widgets : [
      {
        "type" : "metric",
        "x" : 0,
        "y" : 0,
        "width" : 6,
        "height" : 8,
        "properties" : {
          "view" : "pie",
          "metrics" : [
            ["UEC-DOS-INT", "DoSServiceUpdate", "ENV", var.blue_green_environment, "field", "cmsurl", { "label" : "Website", "id" : "m1", "visible" : false }],
            ["...", "postalcode", { "label" : "Postcode", "id" : "m2", "visible" : false }],
            ["...", "postaladdress", { "label" : "Address", "id" : "m3", "visible" : false }],
            ["...", "cmstelephoneno", { "label" : "Public Phone", "id" : "m4", "visible" : false }],
            ["...", "cmseastings", { "label" : "Easting", "id" : "m5", "visible" : false }],
            ["...", "cmsnorthings", { "label" : "Northing", "id" : "m6", "visible" : false }],
            ["...", "cmsorgtown", { "label" : "Town", "id" : "m7", "visible" : false }],
            ["...", "latitude", { "label" : "Latitude", "id" : "m8", "visible" : false }],
            ["...", "longitude", { "label" : "Longitutde", "id" : "m9", "visible" : false }],
            ["...", "cmsorgstatus", { "label" : "Status", "id" : "m10", "visible" : false }],
            ["...", "cmsopentimemonday", { "label" : "Monday", "id" : "m11", "visible" : false }],
            ["...", "cmsopentimetuesday", { "label" : "Tuesday", "id" : "m12", "visible" : false }],
            ["...", "cmsopentimewednesday", { "label" : "Wednesday", "id" : "m13", "visible" : false }],
            ["...", "cmsopentimethursday", { "label" : "Thursday", "id" : "m14", "visible" : false }],
            ["...", "cmsopentimefriday", { "label" : "Friday", "id" : "m15", "visible" : false }],
            ["...", "cmsopentimesaturday", { "label" : "Saturday", "id" : "m16", "visible" : false }],
            ["...", "cmsopentimesunday", { "label" : "Sunday", "id" : "m17", "visible" : false }],
            [{ "expression" : "m1+m2+m3+m4+m5+m6+m7+m8+m9+m10", "label" : "Demographic Updates", "color" : "#1f77b4" }],
            [{ "expression" : "m11+m12+m13+m14+m15+m16+m17", "label" : "Standard Opening Times", "color" : "#ff7f0e" }],
            ["UEC-DOS-INT", "DoSServiceUpdate", "ENV", var.blue_green_environment, "field", "cmsopentimespecified", { "label" : "Specified Opening Times", "color" : "#2ca02c" }],
            ["UEC-DOS-INT", "DoSServiceUpdate", "ENV", var.blue_green_environment, "field", "cmssgsdid", { "label" : "Clinical", "color" : "#9467bd" }],
          ],
          "stacked" : false,
          "region" : var.aws_region,
          "period" : 3600,
          "stat" : "Sum",
          "title" : "DoS Service Updates (Last Hour)",
          "timezone" : "LOCAL"
        }
      },
      {
        "type" : "metric",
        "x" : 6,
        "y" : 0,
        "width" : 18,
        "height" : 4,
        "properties" : {
          "sparkline" : true,
          "view" : "singleValue",
          "metrics" : [
            ["UEC-DOS-INT", "DoSAllServiceUpdates", "ENV", var.blue_green_environment, { "label" : "All", "color" : "#000000" }],
            [".", "DoSServiceUpdate", ".", var.blue_green_environment, "field", "cmsurl", { "label" : "Website", "id" : "m1", "visible" : false }],
            ["...", "postalcode", { "label" : "Postcode", "id" : "m2", "visible" : false }],
            ["...", "postaladdress", { "label" : "Address", "id" : "m3", "visible" : false }],
            ["...", "cmstelephoneno", { "label" : "Public Phone", "id" : "m4", "visible" : false }],
            ["...", "cmseastings", { "label" : "Easting", "id" : "m5", "visible" : false }],
            ["...", "cmsnorthings", { "label" : "Northing", "id" : "m6", "visible" : false }],
            ["...", "cmsorgtown", { "label" : "Town", "id" : "m7", "visible" : false }],
            ["...", "latitude", { "label" : "Latitude", "id" : "m8", "visible" : false }],
            ["...", "longitude", { "label" : "Longitutde", "id" : "m9", "visible" : false }],
            ["...", "cmsorgstatus", { "label" : "Status", "id" : "m10", "visible" : false }],
            ["...", "cmsopentimemonday", { "label" : "Monday", "id" : "m11", "visible" : false }],
            ["...", "cmsopentimetuesday", { "label" : "Tuesday", "id" : "m12", "visible" : false }],
            ["...", "cmsopentimewednesday", { "label" : "Wednesday", "id" : "m13", "visible" : false }],
            ["...", "cmsopentimethursday", { "label" : "Thursday", "id" : "m14", "visible" : false }],
            ["...", "cmsopentimefriday", { "label" : "Friday", "id" : "m15", "visible" : false }],
            ["...", "cmsopentimesaturday", { "label" : "Saturday", "id" : "m16", "visible" : false }],
            ["...", "cmsopentimesunday", { "label" : "Sunday", "id" : "m17", "visible" : false }],
            [{ "expression" : "m1+m2+m3+m4+m5+m6+m7+m8+m9+m10", "label" : "Demographic Updates", "color" : "#1f77b4" }],
            [{ "expression" : "m11+m12+m13+m14+m15+m16+m17", "label" : "Standard Opening Times", "color" : "#ff7f0e" }],
            ["UEC-DOS-INT", "DoSServiceUpdate", "ENV", var.blue_green_environment, "field", "cmsopentimespecified", { "label" : "Specified Opening Times", "color" : "#2ca02c" }],
            ["...", "cmssgsdid", { "label" : "Clinical", "color" : "#9467bd" }],
          ],
          "stacked" : false,
          "region" : var.aws_region,
          "period" : 3600,
          "stat" : "Sum",
          "title" : "DoS Service Updates (Per Hour)",
          "timezone" : "LOCAL"
        }
      },
      { "type" : "metric",
        "x" : 6,
        "y" : 4,
        "width" : 18,
        "height" : 4,
        "properties" : {
          "sparkline" : true,
          "view" : "singleValue",
          "metrics" : [
            ["UEC-DOS-INT", "DoSServiceUpdate", "ENV", var.blue_green_environment, "field", "cmsurl", { "label" : "Website" }],
            ["...", "postalcode", { "label" : "Postcode" }],
            ["...", "postaladdress", { "label" : "Address" }],
            ["...", "cmstelephoneno", { "label" : "Public Phone", }],
            ["...", "cmseastings", { "label" : "Easting" }],
            ["...", "cmsnorthings", { "label" : "Northing" }],
            ["...", "cmsorgtown", { "label" : "Town" }],
            ["...", "latitude", { "label" : "Latitude" }],
            ["...", "longitude", { "label" : "Longitutde" }],
            ["...", "cmsorgstatus", { "label" : "Status" }],
            ["...", "cmsopentimemonday", { "label" : "Monday" }],
            ["...", "cmsopentimetuesday", { "label" : "Tuesday" }],
            ["...", "cmsopentimewednesday", { "label" : "Wednesday" }],
            ["...", "cmsopentimethursday", { "label" : "Thursday" }],
            ["...", "cmsopentimefriday", { "label" : "Friday" }],
            ["...", "cmsopentimesaturday", { "label" : "Saturday" }],
            ["...", "cmsopentimesunday", { "label" : "Sunday" }],
            ["...", "cmsopentimespecified", { "label" : "Specified Opening Times" }],
            ["...", "cmssgsdid", { "label" : "Clinical" }],
          ]
          "sparkline" : true,
          "period" : 900,
          "region" : var.aws_region,
          "stacked" : true,
          "stat" : "Sum",
          "title" : "DoS Individual Service Updates",
          "view" : "timeSeries",
          "timezone" : "LOCAL"
          "yAxis" : {
            "left" : {
              "label" : "Updates",
              "showUnits" : false
          } }
        }
      }
    ]
    }
  )
}
