resource "aws_kms_key" "signing_key" {
  description              = "${var.shared_environment} signing key for default region"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  policy                   = data.aws_iam_policy_document.kms_policy.json
  deletion_window_in_days  = 7
  is_enabled               = true
  enable_key_rotation      = true
}

resource "aws_kms_alias" "signing_key" {
  name          = "alias/${var.signing_key_alias}"
  target_key_id = aws_kms_key.signing_key.key_id
}

resource "aws_kms_key" "route53_health_check_alarm_region_signing_key" {
  provider                 = aws.route53_health_check_alarm_region
  description              = "${var.shared_environment} alarm region signing key"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  policy                   = data.aws_iam_policy_document.kms_policy.json
  deletion_window_in_days  = 7
  is_enabled               = true
  enable_key_rotation      = true
}

resource "aws_kms_alias" "alarm_region_signing_key" {
  provider      = aws.route53_health_check_alarm_region
  name          = "alias/${var.route53_health_check_alarm_region_signing_key_alias}"
  target_key_id = aws_kms_key.route53_health_check_alarm_region_signing_key.key_id
}
