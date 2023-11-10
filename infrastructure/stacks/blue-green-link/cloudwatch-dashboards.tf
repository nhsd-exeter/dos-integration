resource "aws_cloudwatch_dashboard" "cloudwatch_monitoring_dashboard" {
  dashboard_name = var.cloudwatch_monitoring_dashboard_name
  dashboard_body = jsonencode(
    {
      "variables" : [
        {
          "type" : "pattern",
          "pattern" : "((?<=\")|(?<=-))${var.blue_green_environment}",
          "inputType" : "select",
          "id" : "CloudWatchVersionVariable",
          "label" : "BlueGreenVersion",
          "defaultValue" : var.blue_green_environment,
          "visible" : true,
          "values" : [
            {
              "value" : var.blue_green_environment,
              "label" : var.blue_green_environment
            },
            {
              "value" : var.previous_blue_green_environment,
              "label" : var.previous_blue_green_environment
            }
          ]
        }
      ],
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
          "width" : 4,
          "y" : 0,
          "x" : 3,
          "type" : "metric",
          "properties" : {
            "view" : "gauge",
            "metrics" : [
              ["UEC-DOS-INT", "QueueToDoSLatency", "ENV", var.blue_green_environment, { "region" : var.aws_region, "color" : "#69ae34" }]
            ],
            "yAxis" : {
              "left" : {
                "min" : 0,
                "max" : 120000
              }
            },
            "region" : var.aws_region,
            "start" : "-PT5M",
            "end" : "P0D"
            "annotations" : {
              "horizontal" : [
                {
                  "color" : "#d62728",
                  "label" : "Above SLA",
                  "value" : 120000,
                  "fill" : "above"
                }
              ]
            },
            "timezone" : "LOCAL"
            "setPeriodToTimeRange" : true,
            "title" : "Message Latency"
          }
        },
        {
          "height" : 6,
          "width" : 4,
          "y" : 0,
          "x" : 7,
          "type" : "metric",
          "properties" : {
            "metrics" : [
              ["UEC-DOS-INT", "QueueToDoSLatency", "ENV", var.blue_green_environment, { "region" : var.aws_region, "color" : "#69ae34" }]
            ],
            "annotations" : {
              "horizontal" : [
                {
                  "color" : "#d62728",
                  "label" : "Above SLA",
                  "value" : 120000,
                  "fill" : "above"
                }
              ]
            },
            "start" : "-PT1H",
            "end" : "P0D",
            "period" : 3600,
            "region" : var.aws_region
            "setPeriodToTimeRange" : true,
            "title" : "Message Latency",
            "view" : "gauge",
            "yAxis" : {
              "left" : {
                "max" : 120000,
                "min" : 0
              }
            },
            "stat" : "Average",
            "timezone" : "LOCAL"
          }
        },
        {
          "height" : 6,
          "width" : 4,
          "y" : 0,
          "x" : 11,
          "type" : "metric",
          "properties" : {
            "metrics" : [
              ["UEC-DOS-INT", "QueueToDoSLatency", "ENV", var.blue_green_environment, { "region" : var.aws_region, "color" : "#69ae34" }]
            ],
            "annotations" : {
              "horizontal" : [
                {
                  "color" : "#d62728",
                  "label" : "Above SLA",
                  "value" : 120000,
                  "fill" : "above"
                }
              ]
            },
            "period" : 86400,
            "start" : "-PT24H",
            "end" : "P0D",
            "region" : var.aws_region
            "setPeriodToTimeRange" : true,
            "title" : "Message Latency",
            "view" : "gauge",
            "yAxis" : {
              "left" : {
                "max" : 120000,
                "min" : 0
              }
            },
            "stat" : "Average"
            "timezone" : "LOCAL"
          }
        },
        {
          "type" : "metric",
          "height" : 6,
          "width" : 9,
          "y" : 0,
          "x" : 15,
          "properties" : {
            "sparkline" : true,
            "view" : "singleValue",
            "metrics" : [
              ["UEC-DOS-INT", "UpdateRequestSuccess", "ENV", var.blue_green_environment, { "region" : var.aws_region, "color" : "#2ca02c", "label" : "DoS Service Update Success" }],
              [".", "UpdateRequestFailed", ".", var.blue_green_environment, { "region" : var.aws_region, "color" : "#d62728", "label" : "DoS Service Update Failed" }],
              [".", "ChangeEventReceived", ".", var.blue_green_environment, { "region" : var.aws_region, "color" : "#1f77b4", "label" : "Change Event Received" }],
              [".", "UpdateRequestSent", ".", var.blue_green_environment, { "label" : "Update Requests Sent", "color" : "#b088f5" }],
              [".", "DoSAllServiceUpdates", ".", var.blue_green_environment, { "label" : "All DoS Data Item Updates", "color" : "#000000" }],
              [".", "QualityCheckerIssueFound", ".", var.blue_green_environment, { "label" : "Quality Checker Issue Found", "color" : "#f89256" }],
            ],
            "stacked" : false,
            "region" : var.aws_region,
            "period" : 3600,
            "stat" : "Sum",
            "title" : "System Health",
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
              ["AWS/ApiGateway", "Count", "ApiName", var.di_endpoint_api_gateway_name]
            ],
            "period" : 60,
            "stat" : "Sum",
            "region" : var.aws_region,
            "view" : "timeSeries",
            "stacked" : false,
            "title" : "DI Endpoint Requests"
            "yAxis" : {
              "left" : {
                "showUnits" : false,
                "label" : "Count"
              }
            }
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
              ["AWS/Lambda", "Errors", "FunctionName", var.change_event_dlq_handler_lambda, { "id" : "m11", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.change_event_dlq_handler_lambda, { "id" : "m12", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m11/m12) * 100", "label" : "Change Event DLQ Handler", region : var.aws_region, "color" : "#1f77b4" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.dos_db_update_dlq_handler_lambda, { "id" : "m21", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.dos_db_update_dlq_handler_lambda, { "id" : "m22", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m21/m22) * 100", "label" : "DoS DB Update Handler", region : var.aws_region, "color" : "#ff7f0e" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.event_replay_lambda, { "id" : "m31", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.event_replay_lambda, { "id" : "m32", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m31/m32) * 100", "label" : "Event Replay", region : var.aws_region, "color" : "#2ca02c" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.ingest_change_event_lambda, { "id" : "m41", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.ingest_change_event_lambda, { "id" : "m42", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m41/m42) * 100", "label" : "Ingest Change Event", region : var.aws_region, "color" : "#d62728" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.send_email_lambda, { "id" : "m51", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.send_email_lambda, { "id" : "m52", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m51/m52) * 100", "label" : "Send Email", region : var.aws_region, "color" : "#9467bd" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.service_matcher_lambda, { "id" : "m61", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.service_matcher_lambda, { "id" : "m62", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m61/m62) * 100", "label" : "Service Matcher", region : var.aws_region, "color" : "#8c564b" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.service_sync_lambda, { "id" : "m71", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.service_sync_lambda, { "id" : "m72", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m71/m72) * 100", "label" : "Service Sync", region : var.aws_region, "color" : "#e377c2" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.slack_messenger_lambda, { "id" : "m81", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.slack_messenger_lambda, { "id" : "m82", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m81/m82) * 100", "label" : "Slack Messenger", region : var.aws_region, "color" : "#bcbd22" }],
              ["AWS/Lambda", "Errors", "FunctionName", var.quality_checker_lambda, { "id" : "m91", "stat" : "Sum", "visible" : false }],
              [".", "Invocations", ".", var.quality_checker_lambda, { "id" : "m92", "stat" : "Sum", "visible" : false }],
              [{ "expression" : "(m91/m92) * 100", "label" : "Quality Checker", region : var.aws_region, "color" : "#95a5a6" }]
            ],
            "region" : var.aws_region,
            "title" : "Lambda Error Rates",
            "period" : 60
            "yAxis" : {
              "left" : {
                "label" : "Percentage",
                "showUnits" : false
            } },
            "annotations" : {
              "horizontal" : [
                {
                  "label" : "Too Many Errors",
                  "value" : 0.01,
                  "fill" : "above"
                }
              ]
            }
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
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.ingest_change_event_lambda],
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
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.service_matcher_lambda],
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
              ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", var.service_sync_lambda],
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
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.change_event_queue],
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
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.holding_queue],
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
              ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.update_request_queue],
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
              ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.dos_db_writer_name, { stat : "Maximum" }],
              ["...", var.dos_db_reader_name, { stat : "Maximum" }]
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
              ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.dos_db_writer_name],
              ["...", var.dos_db_reader_name]
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
              ["AWS/RDS", "AuroraReplicaLag", "DBClusterIdentifier", var.dos_db_cluster_name]
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
            "timezone" : "LOCAL",
            "yAxis" : {
              "left" : {
                "showUnits" : false,
                "label" : "Count"
              }
            }
          }
        },
        {
          "type" : "metric",
          "x" : 0,
          "y" : 30,
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
          "y" : 30,
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
          "y" : 34,
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
