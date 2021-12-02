resource "aws_api_gateway_rest_api" "dos_api_gateway" {
  name        = var.dos_api_gateway_name
  description = ""
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "dos_api_gateway_resource" {
  parent_id   = aws_api_gateway_rest_api.dos_api_gateway.root_resource_id
  path_part   = "change-request"
  rest_api_id = aws_api_gateway_rest_api.dos_api_gateway.id
}

resource "aws_api_gateway_method" "dos_api_gateway_method" {
  http_method   = "POST"
  resource_id   = aws_api_gateway_resource.dos_api_gateway_resource.id
  rest_api_id   = aws_api_gateway_rest_api.dos_api_gateway.id
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.dos_api_gateway_authoriser.id
}

resource "aws_api_gateway_integration" "dos_api_gateway_mock_integration" {
  http_method = aws_api_gateway_method.dos_api_gateway_method.http_method
  resource_id = aws_api_gateway_resource.dos_api_gateway_resource.id
  rest_api_id = aws_api_gateway_rest_api.dos_api_gateway.id
  type        = "MOCK"
  request_templates = {
    "application/json" = jsonencode(
      {
        statusCode = 200
      }
    )
  }
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.dos_api_gateway.id
  resource_id = aws_api_gateway_resource.dos_api_gateway_resource.id
  http_method = aws_api_gateway_method.dos_api_gateway_method.http_method
  status_code = 200
}

resource "aws_api_gateway_integration_response" "dos_api_gateway_mock_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.dos_api_gateway.id
  resource_id = aws_api_gateway_resource.dos_api_gateway_resource.id
  http_method = aws_api_gateway_method.dos_api_gateway_method.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code

  response_templates = {
    "application/json" = <<EOF
"body": "{\"dosChanges\": [{\"changeId\": \"Change_ID_1_here\"},{\"changeId\": \"Change_ID_2_here\"}]}"
EOF
  }
}

resource "aws_api_gateway_deployment" "dos_api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.dos_api_gateway.id
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.dos_api_gateway_resource,
      aws_api_gateway_method.dos_api_gateway_method,
      aws_api_gateway_integration.dos_api_gateway_mock_integration,
      aws_api_gateway_integration_response.dos_api_gateway_mock_integration_response,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "dos_api_gateway_stage" {
  deployment_id = aws_api_gateway_deployment.dos_api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.dos_api_gateway.id
  stage_name    = var.dos_api_gateway_stage
}

resource "aws_api_gateway_usage_plan" "dos_api_gateway_usage_plan" {
  name        = "${var.dos_api_gateway_name}-usage-plan"
  description = "Usage Plan is for the DoS API Gateway mock for ${var.dos_api_gateway_name}"

  api_stages {
    api_id = aws_api_gateway_rest_api.dos_api_gateway.id
    stage  = aws_api_gateway_stage.dos_api_gateway_stage.stage_name
  }

  throttle_settings {
    rate_limit  = 3
    burst_limit = 6
  }
}

resource "aws_api_gateway_authorizer" "dos_api_gateway_authoriser" {
  name                   = var.dos_api_gateway_authoriser
  rest_api_id            = aws_api_gateway_rest_api.dos_api_gateway.id
  authorizer_uri         = aws_lambda_function.authoriser_lambda.invoke_arn
  authorizer_credentials = aws_iam_role.invocation_authoriser_role.arn
}

resource "aws_iam_role" "invocation_authoriser_role" {
  name = "${var.dos_api_gateway_authoriser}-role"
  path = "/"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "invocation_authoriser_policy" {
  name = "${var.dos_api_gateway_authoriser}-policy"
  role = aws_iam_role.invocation_authoriser_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "lambda:InvokeFunction",
      "Effect": "Allow",
      "Resource": "${aws_lambda_function.authoriser_lambda.arn}"
    }
  ]
}
EOF
}
