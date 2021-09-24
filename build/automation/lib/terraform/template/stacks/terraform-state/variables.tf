# ==============================================================================
# User variables

variable "terraform_state_bucket_name" { description = "The S3 bucket name to store Terraform state" }
variable "terraform_state_table_name" { description = "The DynamoDB table name to acquire Terraform lock" }
