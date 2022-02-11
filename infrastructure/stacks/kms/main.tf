
resource "aws_kms_key" "ddb_kms_key" {
  description              = "KMS key for DynamoDB"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  policy                   = data.aws_iam_policy_document.key.json
  is_enabled               = true
  enable_key_rotation      = false
  deletion_window_in_days  = 7
}

resource "aws_kms_alias" "ddb_kms_key" {
  name          = "alias/${var.ddb_kms_key_alias}"
  target_key_id = aws_kms_key.ddb_kms_key.key_id
}


resource "aws_kms_key" "sqs_kms_key" {
  description              = "KMS key for SQS"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  policy                   = data.aws_iam_policy_document.key.json
  is_enabled               = true
  enable_key_rotation      = false
  deletion_window_in_days  = 7
}

resource "aws_kms_alias" "sqs_kms_key" {
  name          = "alias/${var.sqs_kms_key_alias}"
  target_key_id = aws_kms_key.sqs_kms_key.key_id
}
