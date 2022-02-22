resource "aws_cloudwatch_event_bus" "change_request_bus" {
  name = var.eventbridge_bus_name
}

resource "aws_cloudwatch_event_rule" "change_request_rule" {
  name           = var.change_request_eventbridge_rule_name
  description    = "Rule to trigger on change request received into the bus"
  event_bus_name = var.eventbridge_bus_name
  event_pattern  = <<EOF
{
  "detail-type": ["change-request"]
}
EOF
  depends_on     = [aws_cloudwatch_event_bus.change_request_bus]
}

resource "aws_sqs_queue" "eventbridge_dlq_queue_from_event_bus" {
  name                      = var.dead_letter_queue_from_event_bus_name
  fifo_queue                = false
  sqs_managed_sse_enabled   = true
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_lambda_event_source_mapping" "dead_letter_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.eventbridge_dlq_queue_from_event_bus.arn
  enabled          = true
  function_name    = data.aws_lambda_function.eventbridge_dlq_handler.arn
}

resource "aws_sqs_queue_policy" "eventbridge_dlq_queue_from_event_bus_policy" {
  queue_url = aws_sqs_queue.eventbridge_dlq_queue_from_event_bus.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "sqspolicy",
  "Statement": [
    {
      "Sid": "First",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "${aws_sqs_queue.eventbridge_dlq_queue_from_event_bus.arn}",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "${aws_cloudwatch_event_rule.change_request_rule.arn}"
        }
      }
    }
  ]
}
POLICY
}
resource "aws_cloudwatch_event_target" "api_destination_target" {
  rule           = aws_cloudwatch_event_rule.change_request_rule.name
  arn            = aws_cloudwatch_event_api_destination.dos_api_gateway_destination.arn
  event_bus_name = var.eventbridge_bus_name
  role_arn       = aws_iam_role.target_role.arn
  input_path     = "$.detail"
  depends_on     = [aws_cloudwatch_event_api_destination.dos_api_gateway_destination]
  dead_letter_config {
    arn = aws_sqs_queue.eventbridge_dlq_queue_from_event_bus.arn
  }
}

resource "aws_cloudwatch_event_connection" "dos_api_gateway_connection" {
  name               = var.dos_api_gateway_eventbridge_connection_name
  description        = "Connection details for DoS API Gateway"
  authorization_type = "API_KEY"

  auth_parameters {
    api_key {
      key   = "x-api-key"
      value = jsondecode(data.aws_secretsmanager_secret_version.change_request_receiver.secret_string)[var.change_request_receiver_api_key_key]
    }
  }
}

resource "aws_cloudwatch_event_api_destination" "dos_api_gateway_destination" {
  name                             = var.dos_api_gateway_api_destination_name
  description                      = "API Destination of the DoS API Gateway"
  invocation_endpoint              = var.dos_api_gateway_api_destination_url
  http_method                      = "POST"
  invocation_rate_limit_per_second = 3
  connection_arn                   = aws_cloudwatch_event_connection.dos_api_gateway_connection.arn
}

resource "aws_iam_role" "target_role" {
  name               = var.eventbridge_target_role_name
  path               = "/"
  description        = "Role for the eventbridge target"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "target_role_policy" {
  name   = var.eventbridge_target_policy_name
  role   = aws_iam_role.target_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "kms:*",
      "Resource": "${aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:*",
        "events:*"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "${aws_sqs_queue.eventbridge_dlq_queue_from_event_bus.arn}"
    }
  ]
}
EOF
}
