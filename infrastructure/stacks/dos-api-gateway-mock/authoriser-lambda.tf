resource "aws_lambda_function" "authoriser_lambda" {
  function_name = var.authoriser_lambda_name
  role          = aws_iam_role.authoriser_lambda_role.arn
  package_type  = "Image"
  timeout       = "30"
  image_uri     = "${var.aws_same_account_docker_registry}/authoriser:${var.image_version}"
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = {
      "DOS_API_GATEWAY_CREDENTIALS_SECRET_NAME" = var.dos_api_gateway_secret
      "DOS_API_GATEWAY_USERNAME_KEY"            = var.dos_api_gateway_secret_username_key
      "DOS_API_GATEWAY_PASSWORD_KEY"            = var.dos_api_gateway_secret_password_key
      "POWERTOOLS_SERVICE_NAME"                 = var.powertools_service_name
    }
  }
  depends_on = [
    aws_iam_role.authoriser_lambda_role,
    aws_iam_role_policy.authoriser_lambda_role_policy,
    aws_cloudwatch_log_group.authoriser_lambda_log_group
  ]
}

resource "aws_lambda_function_event_invoke_config" "authoriser_lambda_invoke_config" {
  function_name          = aws_lambda_function.authoriser_lambda.function_name
  maximum_retry_attempts = 0
}

resource "aws_iam_role" "authoriser_lambda_role" {
  name               = "${var.authoriser_lambda_name}-role"
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

resource "aws_iam_role_policy" "authoriser_lambda_role_policy" {
  name   = "${var.authoriser_lambda_name}-role-policy"
  role   = aws_iam_role.authoriser_lambda_role.name
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

resource "aws_cloudwatch_log_group" "authoriser_lambda_log_group" {
  name              = "/aws/lambda/${var.authoriser_lambda_name}"
  retention_in_days = "1"
}
