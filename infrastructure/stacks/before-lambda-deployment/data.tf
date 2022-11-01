# ##############
# # OTHER
# ##############

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.vpc_terraform_state_key
    region = var.aws_region
  }
}

# ##############
# # RDS
# ##############

data "aws_db_instance" "dos_db" {
  db_instance_identifier = var.dos_db_name
}

data "aws_db_instance" "dos_db_replica" {
  db_instance_identifier = var.dos_db_replica_name
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
