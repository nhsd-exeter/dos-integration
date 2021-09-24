# ==============================================================================
# Data

data "terraform_remote_state" "terraform-state" {
  backend = "s3"
  config = {
    key    = "${var.terraform_state_key_shared}/terraform-state/terraform.state"
    bucket = var.terraform_state_store
    region = var.aws_region
  }
}

# ==============================================================================
# Terraform state keys and store set by the Make DevOps automation scripts

variable "terraform_state_store" {}
variable "terraform_state_key_shared" {}
