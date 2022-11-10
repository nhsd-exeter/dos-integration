resource "aws_lambda_event_source_mapping" "change_event_event_source_mapping" {
  batch_size       = 1
  event_source_arn = data.aws_sqs_queue.change_event_queue.arn
  enabled          = true
  function_name    = data.aws_lambda_function.ingest_change_event.arn
}

resource "aws_lambda_event_source_mapping" "change_event_dlq_event_source_mapping" {
  batch_size       = 1
  event_source_arn = data.aws_sqs_queue.change_event_dlq.arn
  enabled          = true
  function_name    = data.aws_lambda_function.change_event_dlq_handler.arn
}
