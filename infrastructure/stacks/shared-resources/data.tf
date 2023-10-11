# ##############
# # SECRETS
# ##############

data "aws_secretsmanager_secret_version" "api_key" {
  secret_id = var.api_gateway_api_key_name
}

data "aws_secretsmanager_secret_version" "ip_address_secret" {
  secret_id = var.ip_address_secret
}

# ##############
# # IAM
# ##############

data "aws_iam_policy_document" "kms_policy" {
  #checkov:skip=CKV_AWS_109
  #checkov:skip=CKV_AWS_111
  #checkov:skip=CKV_AWS_290
  #checkov:skip=CKV_AWS_356
  policy_id     = null
  source_json   = null
  override_json = null
  version       = "2012-10-17"
  statement {
    sid    = null
    effect = "Allow"
    principals {
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.aws_sso_role}"
      ]
      type = "AWS"
    }
    actions = [
      "kms:*"
    ]
    not_actions = []
    resources = [
      "*"
    ]
    not_resources = []
  }
  statement {
    sid    = null
    effect = "Allow"
    principals {
      identifiers = [
        "cloudwatch.amazonaws.com"
      ]
      type = "Service"
    }
    actions = [
      "kms:*"
    ]
    not_actions = []
    resources = [
      "*"
    ]
    not_resources = []
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
