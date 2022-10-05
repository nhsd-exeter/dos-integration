# TODO: Look in to rotating kms keeps
#tfsec:ignore:aws-kms-auto-rotate-keys:2022-01-01
resource "aws_kms_key" "signing_key" {
  description              = "${var.environment} signing key for default region"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  policy                   = data.aws_iam_policy_document.kms_policy.json
  deletion_window_in_days  = 7
  is_enabled               = true
  enable_key_rotation      = false
}

resource "aws_kms_alias" "signing_key" {
  name          = "alias/${var.signing_key_alias}"
  target_key_id = aws_kms_key.signing_key.key_id
}

#tfsec:ignore:aws-kms-auto-rotate-keys:2022-01-01
resource "aws_kms_key" "alarm_region_signing_key" {
  provider                 = aws.alarm-region
  description              = "${var.environment} alarm region signing key"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  policy                   = data.aws_iam_policy_document.kms_policy.json
  deletion_window_in_days  = 7
  is_enabled               = true
  enable_key_rotation      = false
}

resource "aws_kms_alias" "alarm_region_signing_key" {
  provider      = aws.alarm-region
  name          = "alias/${var.alarm_region_signing_key_alias}"
  target_key_id = aws_kms_key.alarm_region_signing_key.key_id
}
