resource "aws_sqs_queue" "change_event_queue" {
  name                        = var.change_event_queue
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  message_retention_seconds   = 1209600 # 14 days
  fifo_throughput_limit       = "perMessageGroupId"
  visibility_timeout_seconds  = 30 # Must be same or higher than ingest change event lambda max execution time
  kms_master_key_id           = aws_kms_key.signing_key.key_id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.change_event_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "change_event_dlq" {
  name                      = var.change_event_dlq
  fifo_queue                = true
  kms_master_key_id         = aws_kms_key.signing_key.key_id
  message_retention_seconds = 1209600 # 14 days
}
