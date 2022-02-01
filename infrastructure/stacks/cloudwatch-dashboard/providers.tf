provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region

  default_tags {
    tags = {
      "Profile"     = var.profile
      "Programme"   = var.programme
      "Service"     = var.project_id
      "Product"     = var.project_id
      "Environment" = var.environment
    }
  }
}
