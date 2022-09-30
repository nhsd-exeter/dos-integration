provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      "Profile"            = var.profile
      "Owner"              = var.distribution_list
      "TagVersion"         = "2.0"
      "DataClassification" = var.data_classification
      "Programme"          = var.programme
      "Service"            = var.project_id
      "Product"            = var.project_id
      "Environment"        = var.environment
      "Environment_Type"   = var.aws_account_name
      "PublicFacing"       = "No"
      "ServiceCategory"    = var.service_category
      "Tool"               = "Terraform"
      "Project"            = var.project_display_name
    }
  }
}
