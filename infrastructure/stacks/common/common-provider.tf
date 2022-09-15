provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      "Profile"            = var.profile
      "Owner"              = "TODO"
      "TagVersion"         = "2.0"
      "DataClassification" = "TODO"
      "Programme"          = var.programme
      "Service"            = var.project_id
      "Product"            = var.project_id
      "Environment"        = var.environment
      "Environment_Type"   = var.aws_account_name
      "PublicFacing"       = "No"
      "ServiceCategory"    = ""
      "Tool"               = "Terraform"
      "Project"            = var.project_display_name
    }
  }
}
