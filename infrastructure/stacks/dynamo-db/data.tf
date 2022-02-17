data "aws_kms_key" "ddb_kms_key" {
  key_id = "alias/${var.sign}"
}

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}
