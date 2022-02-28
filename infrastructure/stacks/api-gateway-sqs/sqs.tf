resource "aws_sqs_queue" "di_change_event_fifo_queue" {
  name                        = var.fifo_queue_name
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  message_retention_seconds   = 1209600 # 14 days
  fifo_throughput_limit       = "perMessageGroupId"
  visibility_timeout_seconds  = 10 # Must be same as event processor max execution time
  kms_master_key_id           = data.aws_kms_key.signing_key.key_id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.di_dead_letter_queue_from_fifo_queue.arn
    maxReceiveCount     = 5
  })
  depends_on = [aws_sqs_queue.di_dead_letter_queue_from_fifo_queue]
}


resource "aws_sqs_queue" "di_change_request_fifo_queue" {
  name                        = var.cr_fifo_queue_name
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  message_retention_seconds   = 1209600 # 14 days
  fifo_throughput_limit       = "perMessageGroupId"
  visibility_timeout_seconds  = 10 # Must be same as event processor max execution time
  kms_master_key_id           = data.aws_kms_key.signing_key.key_id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.cr_di_dead_letter_queue_from_fifo_queue.arn
    maxReceiveCount     = 5
  })
  depends_on = [aws_sqs_queue.cr_di_dead_letter_queue_from_fifo_queue]

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
  kms_master_key_id         = data.aws_kms_key.signing_key.key_id
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_sqs_queue" "cr_di_dead_letter_queue_from_fifo_queue" {
  name                      = var.cr_dead_letter_queue_from_fifo_queue_name
  fifo_queue                = true
  kms_master_key_id         = data.aws_kms_key.signing_key.key_id
  message_retention_seconds = 1209600 # 14 days
}

resource "aws_lambda_event_source_mapping" "dead_letter_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.di_dead_letter_queue_from_fifo_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.fifo_dlq_handler.arn
}

resource "aws_lambda_event_source_mapping" "cr_dead_letter_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.cr_di_dead_letter_queue_from_fifo_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.cr_fifo_dlq_handler.arn
}
