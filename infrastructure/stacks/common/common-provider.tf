provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      "DataClassification" = var.data_classification
      "Environment"        = var.environment
      "EnvironmentType"    = var.aws_account_name
      "Owner"              = var.distribution_list
      "Product"            = var.project_id
      "Profile"            = var.profile
      "Programme"          = var.programme
      "Project"            = var.project_display_name
      "ProviderRegion"     = var.aws_region
      "PublicFacing"       = "No"
      "Service"            = var.project_id
      "ServiceCategory"    = var.service_category
      "TagVersion"         = "2.0"
      "Tool"               = "Terraform"
    }
  }
}

provider "aws" {
  region = var.route53_health_check_alarm_region
  alias  = "route53_health_check_alarm_region"
  default_tags {
    tags = {
      "DataClassification" = var.data_classification
      "Environment"        = var.environment
      "EnvironmentType"    = var.aws_account_name
      "Owner"              = var.distribution_list
      "Product"            = var.project_id
      "Profile"            = var.profile
      "Programme"          = var.programme
      "Project"            = var.project_display_name
      "ProviderRegion"     = var.route53_health_check_alarm_region
      "PublicFacing"       = "No"
      "Service"            = var.project_id
      "ServiceCategory"    = var.service_category
      "TagVersion"         = "2.0"
      "Tool"               = "Terraform"
    }
  }
}
