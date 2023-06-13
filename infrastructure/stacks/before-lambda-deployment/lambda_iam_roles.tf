resource "aws_iam_role" "event_replay_role" {
  name               = var.event_replay_role_name
  path               = "/"
  description        = ""
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "event_replay_policy" {
  name   = "event_replay_policy"
  role   = aws_iam_role.event_replay_role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey",
        "kms:Decrypt"
      ],
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    },
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
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:GetQueueUrl"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.project_id}*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*"
    },
    {
      "Effect": "Allow",
      "Action": "dynamodb:Query",
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*/index/gsi_ods_sequence"
    }
  ]
}
EOF
}



resource "aws_iam_role" "slack_messenger_role" {
  name               = var.slack_messenger_role_name
  path               = "/"
  description        = ""
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "slack_messenger_policy" {
  name   = "slack_messenger_policy"
  role   = aws_iam_role.slack_messenger_role.id
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
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": "sns:*",
      "Resource": [
        "arn:aws:sns:${var.aws_region}:${var.aws_account_id}:${var.project_id}-*",
        "arn:aws:sns:${var.route53_health_check_alarm_region}:${var.aws_account_id}:${var.project_id}-*"
      ]
    }
  ]
}
EOF
}

module "service_matcher" {
  source               = "../../modules/lambda-iam-role"
  lambda_name          = var.service_matcher_lambda_name
  use_custom_policy    = true
  custom_lambda_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.holding_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:SendMessageBatch"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.update_request_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey",
        "kms:Decrypt"
      ],
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    }
  ]
}
EOF
}

module "service_sync" {
  source               = "../../modules/lambda-iam-role"
  lambda_name          = var.service_sync_lambda_name
  use_custom_policy    = true
  custom_lambda_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": "sqs:SendMessage",
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.update_request_dlq}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.update_request_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:BatchGetItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*"
    },
    {
      "Effect": "Allow",
      "Action": "dynamodb:Query",
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*/index/gsi_ods_sequence"
    },
    {
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource":"arn:aws:s3:::${var.send_email_bucket_name}/*"
    },
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource":"arn:aws:lambda:${var.aws_region}:${var.aws_account_id}:function:${var.send_email_lambda_name}"
    }
  ]
}
EOF
}

module "change_event_dlq_handler" {
  source               = "../../modules/lambda-iam-role"
  lambda_name          = var.change_event_dlq_handler_lambda_name
  use_custom_policy    = true
  custom_lambda_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource": [
        "arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.change_event_dlq}",
        "arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.holding_queue_dlq}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:BatchGetItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*"
    },
    {
      "Effect": "Allow",
      "Action": "dynamodb:Query",
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*/index/gsi_ods_sequence"
    }
  ]
}
EOF
}

module "dos_db_update_dlq_handler" {
  source               = "../../modules/lambda-iam-role"
  lambda_name          = var.dos_db_update_dlq_handler_lambda_name
  use_custom_policy    = true
  custom_lambda_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.update_request_dlq}"
    }
  ]
}
EOF
}

module "dos_db_handler" {
  # Only deploy when the environment is not prod
  count                = var.profile != "demo" && var.profile != "live" ? 1 : 0
  source               = "../../modules/lambda-iam-role"
  lambda_name          = var.dos_db_handler_lambda_name
  use_custom_policy    = true
  custom_lambda_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:*"
    }
  ]
}
EOF
}

module "send_email" {
  source               = "../../modules/lambda-iam-role"
  lambda_name          = var.send_email_lambda_name
  use_custom_policy    = true
  custom_lambda_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource":[
        "arn:aws:s3:::${var.send_email_bucket_name}",
        "arn:aws:s3:::${var.send_email_bucket_name}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:uec-dos-int-*"
    }
  ]
}
EOF
}

module "ingest_change_event" {
  source               = "../../modules/lambda-iam-role"
  lambda_name          = var.ingest_change_event_lambda_name
  use_custom_policy    = true
  custom_lambda_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey",
        "kms:Decrypt"
      ],
      "Resource": "${data.aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.change_event_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:SendMessageBatch"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.holding_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "appconfig:GetConfiguration",
        "appconfig:StartConfigurationSession",
        "appconfig:GetLatestConfiguration"
        ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:BatchGetItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*"
    },
    {
      "Effect": "Allow",
      "Action": "dynamodb:Query",
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.project_id}*/index/gsi_ods_sequence"
    }
  ]
}
EOF
}
