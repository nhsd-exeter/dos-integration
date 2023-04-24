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
  source                   = "../../modules/s3"
  name                     = var.logs_bucket_name
  project_id               = var.project_id
  acl                      = "log-delivery-write"
  versioning_enabled       = "true"
  force_destroy            = "true"
  control_object_ownership = true
  object_ownership         = "BucketOwnerPreferred"

  attach_policy = true
  policy = jsonencode(
    {
      Action = "s3:PutObject"
      Effect = "Allow"
      Principal = {
        Service = "logging.s3.amazonaws.com"
      }
      Resource = "arn:aws:s3:::${var.logs_bucket_name}/*"
  })
}
