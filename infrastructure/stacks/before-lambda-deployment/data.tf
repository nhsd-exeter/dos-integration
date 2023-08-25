# ##############
# # VPC
# ##############

data "aws_vpc" "texas_vpc" {
  tags = {
    Name = var.aws_vpc_name
  }
}

# ##############
# # KMS
# ##############

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
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

data "aws_security_group" "dos_db_sg" {
  name = var.dos_db_sg_name
}

data "aws_security_group" "dos_db_replica_sg" {
  count = var.dos_db_replica_sg_name != "" ? 1 : 0
  name  = var.dos_db_replica_sg_name
}
