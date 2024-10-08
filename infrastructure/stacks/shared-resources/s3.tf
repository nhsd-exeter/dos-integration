module "di_send_email_bucket" {
  source             = "../../modules/s3"
  name               = var.send_email_bucket_name
  project_id         = var.project_id
  versioning_enabled = "true"
  force_destroy      = "true"
  object_ownership   = "ObjectWriter"

  logging = {
    target_bucket = module.di_logs_bucket.s3_bucket_id
    target_prefix = "s3/send_email_bucket/"
  }

  server_side_encryption_configuration = {
    rule = [{
      apply_server_side_encryption_by_default = {
        kms_master_key_id = aws_kms_key.signing_key.id
        sse_algorithm     = "aws:kms"
      }
    }]
  }
  lifecycle_days_to_expiration = "90"
  lifecycle_expiration_enabled = "true"

  depends_on = [
    module.di_logs_bucket
  ]
}

module "di_logs_bucket" {
  source             = "../../modules/s3"
  name               = var.logs_bucket_name
  project_id         = var.project_id
  versioning_enabled = "true"
  force_destroy      = "true"

  attach_policy = true
  policy        = data.aws_iam_policy_document.logging_bucket.json
}

data "aws_iam_policy_document" "logging_bucket" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["logging.s3.amazonaws.com"]
    }

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "arn:aws:s3:::${var.logs_bucket_name}/*",
      "arn:aws:s3:::${var.logs_bucket_name}/s3/send_email_bucket/*"
    ]
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:s3:::${var.send_email_bucket_name}"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = ["${var.aws_account_id}"]
    }
  }
}
