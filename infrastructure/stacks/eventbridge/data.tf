data "aws_lambda_function" "event_processor" {
  function_name = var.event_processor_lambda_name
}

data "aws_secretsmanager_secret_version" "change_request_receiver" {
  secret_id = var.change_request_receiver_api_key_name
}
