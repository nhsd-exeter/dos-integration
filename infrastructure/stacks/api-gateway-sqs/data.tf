data "terraform_remote_state" "route53" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.route53_terraform_state_key
    region = var.aws_region
  }
}
data "aws_acm_certificate" "issued" {
  domain   = "*.${var.texas_hosted_zone}"
  statuses = ["ISSUED"]
}

data "aws_lambda_function" "event_processor" {
  function_name = var.event_processor_lambda_name
}

data "aws_lambda_function" "fifo_dlq_handler" {
  function_name = var.fifo_dlq_handler_lambda_name
}

data "aws_secretsmanager_secret_version" "api_key" {
  secret_id = var.api_gateway_api_key_name
}

data "aws_secretsmanager_secret_version" "ip_address_secret" {
  secret_id = var.ip_address_secret
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_iam_policy_document" "key" {
  policy_id     = null
  source_json   = null
  override_json = null
  version       = "2012-10-17"
  statement {
    sid    = null
    effect = "Allow"
    principals {
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
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
}
