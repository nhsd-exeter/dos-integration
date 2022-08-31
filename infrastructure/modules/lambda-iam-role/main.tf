resource "aws_iam_role" "lambda_role" {
  name               = "${var.lambda_name}-role"
  path               = "/"
  description        = "Role for Lambda function ${var.lambda_name}"
  assume_role_policy = data.aws_iam_policy_document.lambda-assume-role-policy.json
}

resource "aws_iam_role_policy" "lambda_generic_policy" {
  name   = "lambda-generic-policy"
  role   = aws_iam_role.lambda_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ec2:AssignPrivateIpAddresses",
        "ec2:UnassignPrivateIpAddresses",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeSubnets",
        "ec2:DescribeVpcs",
        "xray:PutTraceSegments",
        "xray:PutTelemetryRecords"
      ],
      "Resource": ["*"]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "lambda_custom_policy" {
  count  = var.use_custom_policy ? 1 : 0
  name   = "${var.lambda_name}-policy"
  role   = aws_iam_role.lambda_role.id
  policy = var.custom_lambda_policy
}
