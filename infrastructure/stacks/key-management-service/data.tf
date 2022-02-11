data "aws_kms_key" "kms_managed_key" {
  key_id = aws_kms_key.kms_key.key_id
}
