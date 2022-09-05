# TODO: Delete after release 3.0
resource "aws_iam_role" "event_processor_role" {
  name               = var.event_processor_role_name
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

resource "aws_iam_role_policy" "event_processor_policy" {
  name   = "event_processor_policy"
  role   = aws_iam_role.event_processor_role.id
  policy = <<EOF
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
      "Action": "appconfig:GetConfiguration",
      "Resource": "*"
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
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.fifo_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:SendMessageBatch"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.cr_fifo_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey",
        "kms:Decrypt"
      ],
      "Resource": "${aws_kms_key.signing_key.arn}"
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
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.change_events_table_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query"
      ],
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.change_events_table_name}/index/gsi_ods_sequence"
    }
  ]
}
EOF
}

resource "aws_iam_role" "event_sender_role" {
  name               = var.event_sender_role_name
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

resource "aws_iam_role_policy" "event_sender_policy" {
  name   = "event_sender_policy"
  role   = aws_iam_role.event_sender_role.id
  policy = <<EOF
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
      "Resource": "${aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": "sqs:SendMessage",
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.cr_dead_letter_queue_from_fifo_queue_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:DeleteMessageBatch"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.cr_fifo_queue_name}"
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
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.change_events_table_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query"
      ],
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.change_events_table_name}/index/gsi_ods_sequence"
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
      "Resource": ["*"]
    }
  ]
}
EOF
}

resource "aws_iam_role" "fifo_dlq_handler_role" {
  name               = var.fifo_dlq_handler_role_name
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

resource "aws_iam_role_policy" "fifo_dlq_handler_policy" {
  name   = "fifo_dlq_handler_policy"
  role   = aws_iam_role.fifo_dlq_handler_role.id
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
        "kms:Decrypt"
      ],
      "Resource": "${aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.dead_letter_queue_from_fifo_queue_name}"
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
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.change_events_table_name}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query"
      ],
      "Resource":"arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/${var.change_events_table_name}/index/gsi_ods_sequence"
    }
  ]
}
EOF
}


resource "aws_iam_role" "cr_fifo_dlq_handler_role" {
  name               = var.cr_fifo_dlq_handler_role_name
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

resource "aws_iam_role_policy" "cr_fifo_dlq_handler_policy" {
  name   = "cr_fifo_dlq_handler_policy"
  role   = aws_iam_role.cr_fifo_dlq_handler_role.id
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
        "kms:Decrypt"
      ],
      "Resource": "${aws_kms_key.signing_key.arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ReceiveMessage"
      ],
      "Resource":"arn:aws:sqs:${var.aws_region}:${var.aws_account_id}:${var.cr_dead_letter_queue_from_fifo_queue_name}"
    }
  ]
}
EOF
}
