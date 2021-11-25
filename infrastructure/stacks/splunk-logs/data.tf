data "aws_kinesis_firehose_delivery_stream" "dos_integration_firehose" {
  name = var.dos_integration_firehose
}

data "aws_iam_role" "firehose_role" {
  name = var.firehose_role
}
