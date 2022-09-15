module "di_send_email_bucket" {
  source             = "../../modules/s3"
  name               = var.send_email_bucket_name
  project_id         = var.project_id
  acl                = "private"
  versioning_enabled = "true"
  force_destroy      = "true"
  server_side_encryption_configuration = {
    rule = [{
      apply_server_side_encryption_by_default = {
        kms_master_key_id = data.aws_kms_key.signing_key.id
        sse_algorithm     = "aws:kms"
      }
    }]
  }
}
