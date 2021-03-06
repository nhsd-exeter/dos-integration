resource "aws_lambda_function_event_invoke_config" "dos_api_gateway_lambda_invoke_config" {
  function_name          = aws_lambda_function.dos_api_gateway_lambda.function_name
  maximum_retry_attempts = 0
}

resource "aws_iam_role" "dos_api_gateway_lambda_role" {
  name               = "${var.dos_api_gateway_lambda_name}-role"
  path               = "/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "dos_api_gateway_lambda_role_policy" {
  name   = "${var.dos_api_gateway_lambda_name}-role-policy"
  role   = aws_iam_role.dos_api_gateway_lambda_role.name
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:Describe*",
        "secretsmanager:Get*",
        "secretsmanager:List*"
      ],
      "Resource": "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:uec-dos-int*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "xray:PutTraceSegments",
        "xray:PutTelemetryRecords",
        "xray:GetSamplingRules",
        "xray:GetSamplingTargets",
        "xray:GetSamplingStatisticSummaries"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}
POLICY
}

#tfsec:ignore:aws-cloudwatch-log-group-customer-key
resource "aws_cloudwatch_log_group" "dos_api_gateway_lambda_log_group" {
  name              = "/aws/lambda/${var.dos_api_gateway_lambda_name}"
  retention_in_days = "1"
}

resource "aws_lambda_function" "dos_api_gateway_lambda" {
  function_name = var.dos_api_gateway_lambda_name
  role          = aws_iam_role.dos_api_gateway_lambda_role.arn
  package_type  = "Image"
  timeout       = "30"
  image_uri     = "${var.docker_registry}/dos-api-gateway:${var.image_version}"
  memory_size   = 1024
  tracing_config {
    mode = "Active"
  }
  depends_on = [
    aws_iam_role.dos_api_gateway_lambda_role,
    aws_iam_role_policy.dos_api_gateway_lambda_role_policy,
    aws_cloudwatch_log_group.dos_api_gateway_lambda_log_group
  ]
  environment {
    variables = {
      "POWERTOOLS_SERVICE_NAME" = var.powertools_service_name
      "CHAOS_MODE"              = var.chaos_mode
    }
  }
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dos_api_gateway_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${var.aws_account_id}:${aws_api_gateway_rest_api.dos_api_gateway.id}/*/${aws_api_gateway_method.dos_api_gateway_method.http_method}${aws_api_gateway_resource.dos_api_gateway_resource.path}"
  depends_on = [
    aws_lambda_function.dos_api_gateway_lambda, aws_api_gateway_deployment.dos_api_gateway_deployment
  ]
}
