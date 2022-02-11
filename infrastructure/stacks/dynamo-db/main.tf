resource "aws_dynamodb_table" "message-history-table" {
  name         = var.change_events_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Id"
  range_key    = "ODSCode"

  server_side_encryption {
    enabled = true
    kms_key_arn = aws_kms_key.ddb_kms_key.arn
  }

  attribute {
    name = "Id"
    type = "S"
  }

  attribute {
    name = "ODSCode"
    type = "S"
  }

  attribute {
    name = "SequenceNumber"
    type = "N"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  global_secondary_index {
    name            = "gsi_ods_sequence"
    hash_key        = "ODSCode"
    range_key       = "SequenceNumber"
    projection_type = "ALL"
  }

}


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