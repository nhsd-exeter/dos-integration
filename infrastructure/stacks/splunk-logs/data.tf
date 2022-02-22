data "aws_kinesis_firehose_delivery_stream" "dos_integration_firehose" {
  name = var.dos_integration_firehose
}

data "aws_iam_role" "firehose_role" {
  name = var.firehose_role
}

data "aws_api_gateway_rest_api" "di_endpoint" {
  name = var.di_endpoint_api_gateway_name
}

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}
