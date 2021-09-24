module "s3" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "1.17.0"
  tags    = var.context.tags

  bucket        = var.bucket_name
  attach_policy = var.attach_policy
  policy        = var.policy

  force_destroy           = false
  acl                     = "private"
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
  versioning = {
    enabled = true
  }
}
