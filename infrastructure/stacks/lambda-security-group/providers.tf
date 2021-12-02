provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region

  default_tags {
    tags = {
      "Programme"   = "uec"
      "Service"     = "uec-dos-int"
      "Product"     = "uec-dos-int"
      "Environment" = var.profile
    }
  }
}
