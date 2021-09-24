module "NAME_TEMPLATE_TO_REPLACE-store" {
  source  = "../../modules/s3"
  context = local.context

  bucket_name = var.terraform_state_bucket_name
}

module "NAME_TEMPLATE_TO_REPLACE-lock" {
  source  = "../../modules/dynamodb"
  context = local.context

  table_name = var.terraform_state_table_name
  hash_key   = "LockID"
  attributes = [
    {
      name = "LockID"
      type = "S"
    }
  ]
}
