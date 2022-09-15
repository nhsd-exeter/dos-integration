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

resource "aws_s3_bucket_notification" "aws-lambda-trigger" {
  bucket = module.di_send_email_bucket.s3_bucket_id
  lambda_function {
    lambda_function_arn = data.aws_lambda_function.send_email.arn
    events              = ["s3:ObjectCreated:*"]
  }
  depends_on = [
    module.di_send_email_bucket
  ]
}

resource "aws_lambda_permission" "send_email_s3_notification_permission" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.send_email.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.di_send_email_bucket.s3_bucket_arn
  depends_on = [
    module.di_send_email_bucket
  ]
}
