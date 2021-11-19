resource "aws_s3_bucket" "artifacts" {
  bucket = "${var.prefix}-pipeline-artifact"
  versioning {
    enabled = true
  }

  force_destroy = true

  lifecycle_rule {
    enabled = true

    expiration {
      days = 30
    }
  }

  tags = {
    provisioned_by = "terraform"
  }
}