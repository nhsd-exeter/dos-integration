provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      "Profile"     = var.profile
      "Programme"   = var.programme
      "Service"     = var.project_id
      "Product"     = var.project_id
      "Environment" = var.environment
    }
  }
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}
