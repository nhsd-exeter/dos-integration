data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.vpc_terraform_state_key
    region = var.aws_region
  }
}

data "aws_db_instance" "dos_db" {
  db_instance_identifier = var.dos_db_name
}

data "aws_db_instance" "dos_db_replica" {
  db_instance_identifier = var.dos_db_replica_name
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_iam_policy_document" "kms_policy" {
  #checkov:skip=CKV_AWS_109
  #checkov:skip=CKV_AWS_111
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
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.developer_role_name}"
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

data "aws_secretsmanager_secret_version" "deployment_secrets" {
  secret_id = var.email_secrets
}
