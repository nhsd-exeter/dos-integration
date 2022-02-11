
resource "aws_kms_key" "kms_key" {
  description         = "KMS Keys for Data Encryption"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  is_enabled               = true
  enable_key_rotation      = true

  tags = {
    service = var.project_id
  }
}

resource "aws_kms_alias" "kms_managed_key_alias" {
  target_key_id = aws_kms_key.kms_key.key_id
  name          = "alias/${var.kms_managed_key_alias}"
}
