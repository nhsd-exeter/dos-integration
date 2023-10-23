# ##############
# # VPC
# ##############

data "aws_vpc" "texas_vpc" {
  tags = {
    Name = var.aws_vpc_name
  }
}

data "aws_subnets" "texas_vpc_private_subnets" {
  filter {
    name   = "tag:Name"
    values = ["${var.aws_vpc_name}-private-${var.aws_region}a", "${var.aws_vpc_name}-private-${var.aws_region}b", "${var.aws_vpc_name}-private-${var.aws_region}c"]
  }
}

# ##############
# # KMS
# ##############

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}

# ##############
# # SQS
# ##############

data "aws_sqs_queue" "change_event_dlq" {
  name = var.change_event_dlq
}

# ##############
# # SNS
# ##############

data "aws_iam_policy_document" "sns_topic_app_alerts_for_slack_access_default_region" {
  statement {
    actions = ["sns:Publish"]
    principals {
      type = "Service"
      identifiers = [
        "cloudwatch.amazonaws.com",
        "codestar-notifications.amazonaws.com"
      ]
    }
    resources = [aws_sns_topic.sns_topic_app_alerts_for_slack_default_region.arn]
  }
}

data "aws_iam_policy_document" "sns_topic_app_alerts_for_slack_access_alarm_region" {
  provider = aws.route53_health_check_alarm_region
  statement {
    actions = ["sns:Publish"]
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
    resources = [aws_sns_topic.sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn]
  }
}

# ##############
# # RDS SG
# ##############

data "aws_security_group" "db_writer_sg" {
  name = var.db_writer_sg_name
}

data "aws_security_group" "db_reader_sg" {
  name = var.db_reader_sg_name
}

# ##############
# # KINESIS
# ##############

data "aws_kinesis_firehose_delivery_stream" "dos_integration_firehose" {
  name = var.dos_integration_firehose
}

data "aws_kinesis_firehose_delivery_stream" "dos_firehose" {
  name = var.dos_firehose
}

# ##############
# # IAM
# ##############

data "aws_iam_role" "di_firehose_role" {
  name = var.di_firehose_role
}

data "aws_iam_role" "dos_firehose_role" {
  name = var.dos_firehose_role
}
