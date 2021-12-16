resource "aws_sqs_queue" "di_change_event_fifo_queue" {
  name                        = var.fifo_queue_name
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  message_retention_seconds   = 1209600 # 14 days
  fifo_throughput_limit       = "perMessageGroupId"
  visibility_timeout_seconds  = 120 # Must be same as event processor max execution time
  sqs_managed_sse_enabled     = true
  # Add DQL trigger here
}

resource "aws_lambda_event_source_mapping" "fifo_event_source_mapping" {
  batch_size       = 1
  event_source_arn = aws_sqs_queue.di_change_event_fifo_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.event_processor.arn
}
