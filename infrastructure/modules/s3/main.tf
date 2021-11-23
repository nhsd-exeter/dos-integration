
resource "aws_iam_role" "this" {

  name = var.bucket_iam_role
  path = "/"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": { "Service": "ec2.amazonaws.com" },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.this.arn]
    }
    sid    = "IAMS3BucketPermissions"
    effect = "Allow"

    resources = ["arn:aws:s3:::${var.name}"]


    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:ListBucketVersions",
    ]
  }

  statement {
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.this.arn]
    }
    sid    = "IAMS3ObjectPermissions"
    effect = "Allow"

    resources = ["arn:aws:s3:::${var.name}/*"]

    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:ListMultipartUploadParts",
      "s3:PutObject",
    ]
  }

  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    effect  = "Deny"
    actions = ["*"]
    resources = [
      "arn:aws:s3:::${var.name}",
      "arn:aws:s3:::${var.name}/*",
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = var.name
  acl    = var.acl

  // S3 bucket-level Public Access Block configuration
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  force_destroy = var.force_destroy

  attach_policy = true
  policy        = data.aws_iam_policy_document.bucket_policy.json

  versioning = {
    enabled = var.versioning_enabled
  }
  logging = {
    target_bucket = var.log_bucket
    target_prefix = "logs/${var.service_name}/${var.name}/"
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Name    = "${var.profile}-${var.name}"
    Service = var.service_name
    Profile = var.profile
  }

  lifecycle_rule = [{
    id      = "transition-to-infrequent-access-storage"
    enabled = var.lifecycle_infrequent_storage_transition_enabled

    prefix = var.lifecycle_infrequent_storage_object_prefix

    transition = [{
      days          = var.lifecycle_days_to_infrequent_storage_transition
      storage_class = "STANDARD_IA"
    }]
    },
    {
      id      = "transition-to-glacier"
      enabled = var.lifecycle_glacier_transition_enabled

      prefix = var.lifecycle_glacier_object_prefix

      transition = [{
        days          = var.lifecycle_days_to_glacier_transition
        storage_class = "GLACIER"
      }]
    },
    {
      id      = "expire-objects"
      enabled = var.lifecycle_expiration_enabled

      prefix = var.lifecycle_expiration_object_prefix

      expiration = {
        days = var.lifecycle_days_to_expiration
      }
    }
  ]
}
