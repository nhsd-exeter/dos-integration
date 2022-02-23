data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}
