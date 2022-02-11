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

data "aws_kms_key" "ddb_kms_key" {
  key_id = "alias/${var.ddb_kms_key_alias}"
}

data "aws_kms_key" "sqs_kms_key" {
  key_id = "alias/${var.sqs_kms_key_alias}"
}
