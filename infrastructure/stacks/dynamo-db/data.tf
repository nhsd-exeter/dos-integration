data "aws_kms_key" "ddb_kms_key" {
  key_id = "alias/${var.ddb_kms_key_alias}"
}
