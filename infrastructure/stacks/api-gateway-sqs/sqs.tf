resource "aws_sqs_queue" "di_change_event_fifo_queue" {
  name                        = var.fifo_queue_name
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  message_retention_seconds   = 1209600 # 14 days
  fifo_throughput_limit       = "perMessageGroupId"
  visibility_timeout_seconds  = 120 # Must be same as event processor max execution time
  sqs_managed_sse_enabled     = true
  kms_master_key_id           = aws_kms_key.sqs_kms_key.key_id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.di_dead_letter_queue_from_fifo_queue.arn
    maxReceiveCount     = 1
  })
  depends_on = [aws_sqs_queue.di_dead_letter_queue_from_fifo_queue]
}

resource "aws_lambda_event_source_mapping" "fifo_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.di_change_event_fifo_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.event_processor.arn
}

resource "aws_sqs_queue" "di_dead_letter_queue_from_fifo_queue" {
  name                      = var.dead_letter_queue_from_fifo_queue_name
  fifo_queue                = true
  sqs_managed_sse_enabled   = true
  kms_master_key_id         = aws_kms_key.sqs_kms_key.key_id
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_lambda_event_source_mapping" "dead_letter_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.di_dead_letter_queue_from_fifo_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.fifo_dlq_handler.arn
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
