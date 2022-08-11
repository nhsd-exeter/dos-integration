resource "aws_sqs_queue" "change_event_queue" {
  name                        = var.change_event_queue_name
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  message_retention_seconds   = 1209600 # 14 days
  fifo_throughput_limit       = "perMessageGroupId"
  visibility_timeout_seconds  = 10 # Must be same as service matcher max execution time
  kms_master_key_id           = data.aws_kms_key.signing_key.key_id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.change_event_dlq.arn
    maxReceiveCount     = 5
  })
  depends_on = [aws_sqs_queue.change_event_dlq]
}


resource "aws_sqs_queue" "update_request_queue" {
  name                        = var.update_request_queue_name
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  message_retention_seconds   = 1209600 # 14 days
  fifo_throughput_limit       = "perMessageGroupId"
  visibility_timeout_seconds  = 30 # Should be same as orchestrator + service sync max execution time
  kms_master_key_id           = data.aws_kms_key.signing_key.key_id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.update_request_dlq.arn
    maxReceiveCount     = 5
  })
  depends_on = [aws_sqs_queue.update_request_dlq]
}

resource "aws_lambda_event_source_mapping" "change_event_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.change_event_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.service_matcher.arn
}

resource "aws_sqs_queue" "change_event_dlq" {
  name                      = var.change_event_dlq
  fifo_queue                = true
  kms_master_key_id         = data.aws_kms_key.signing_key.key_id
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_sqs_queue" "update_request_dlq" {
  name                      = var.update_request_dlq
  fifo_queue                = true
  kms_master_key_id         = data.aws_kms_key.signing_key.key_id
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_lambda_event_source_mapping" "change_event_dlq_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.change_event_dlq.arn
  enabled          = true
  function_name    = data.aws_lambda_function.change_event_dlq_handler.arn
}

resource "aws_lambda_event_source_mapping" "update_request_dlq_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.update_request_dlq.arn
  enabled          = true
  function_name    = data.aws_lambda_function.dos_db_update_dlq_handler.arn
}
