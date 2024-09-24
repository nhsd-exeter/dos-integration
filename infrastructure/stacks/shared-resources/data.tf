# ##############
# # SECRETS
# ##############

data "aws_secretsmanager_secret_version" "api_key" {
  secret_id = var.api_gateway_api_key_name
}

data "aws_secretsmanager_secret_version" "ip_address_secret" {
  secret_id = var.ip_address_secret
}

data "aws_secretsmanager_secret_version" "deployment_secrets" {
  secret_id = var.project_deployment_secrets
}

# ##############
# # IAM
# ##############

data "aws_iam_policy_document" "kms_policy" {
  #checkov:skip=CKV_AWS_109
  #checkov:skip=CKV_AWS_111
  #checkov:skip=CKV_AWS_356
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principals {
      identifiers = var.aws_account_name != "prod" ? [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.aws_sso_role}"
        ] : [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.aws_sso_role}",
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.aws_sso_read_write_role}",
      ]
      type = "AWS"
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    principals {
      identifiers = ["cloudwatch.amazonaws.com", "logs.${var.aws_region}.amazonaws.com", "logs.${var.route53_health_check_alarm_region}.amazonaws.com"]
      type        = "Service"
    }
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "shared_resources_sns_topic_app_alerts_for_slack_access_default_region" {
  statement {
    actions = ["sns:Publish"]
    principals {
      type = "Service"
      identifiers = [
        "cloudwatch.amazonaws.com",
        "codestar-notifications.amazonaws.com"
      ]
    }
    resources = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_default_region.arn]
    condition {
      test     = "StringEquals"
      variable = "sns:Protocol"
      values   = ["https"]
    }
  }
}

data "aws_iam_policy_document" "shared_resources_sns_topic_app_alerts_for_slack_access_alarm_region" {
  provider = aws.route53_health_check_alarm_region
  statement {
    actions = ["sns:Publish"]
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
    resources = [aws_sns_topic.shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region.arn]
    condition {
      test     = "StringEquals"
      variable = "sns:Protocol"
      values   = ["https"]
    }
  }
}

data "aws_iam_role" "di_firehose_role" {
  name = var.di_firehose_role
}

# ##############
# # ROUTE 53
# ##############
data "aws_route53_zone" "texas_hosted_zone" {
  name = var.texas_hosted_zone
}

data "aws_acm_certificate" "issued" {
  domain   = "*.${var.texas_hosted_zone}"
  statuses = ["ISSUED"]
}

# ##############
# # KINESIS
# ##############

data "aws_kinesis_firehose_delivery_stream" "dos_integration_firehose" {
  name = var.dos_integration_firehose
}

# ##############
# # OTHER
# ##############

data "aws_caller_identity" "current" {}
