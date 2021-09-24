module "dynamodb" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "0.11.0"
  tags    = var.context.tags

  name       = var.table_name
  hash_key   = var.hash_key
  attributes = var.attributes

  server_side_encryption_enabled = true
  point_in_time_recovery_enabled = true

  # range_key      = var.range_key
  # billing_mode   = var.billing_mode
  # read_capacity  = var.read_capacity
  # write_capacity = var.write_capacity
}
