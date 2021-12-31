resource "aws_dynamodb_table" "message-history-table" {
  name         = var.change_events_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "request_id"
  range_key    = "ods_code"

  attribute {
    name = "request_id"
    type = "S"
  }

  attribute {
    name = "ods_code"
    type = "S"
  }

  attribute {
    name = "event_received_time"
    type = "N"
  }

  ttl {
    attribute_name = "event_expiry_epoch"
    enabled        = true
  }

  global_secondary_index {
    name            = "gsi_event_received_time"
    hash_key        = "ods_code"
    range_key       = "event_received_time"
    projection_type = "ALL"
  }

  tags = {
    service = var.project_id
  }
}

resource "aws_dynamodb_table" "ods_sequence_pointer" {
  name         = var.ods_sequence_pointer
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "ods_code"
  range_key    = "sequence_pointer"

  attribute {
    name = "ods_code"
    type = "S"
  }

  attribute {
    name = "sequence_pointer"
    type = "S"
  }

  tags = {
    service = var.project_id
  }
}
