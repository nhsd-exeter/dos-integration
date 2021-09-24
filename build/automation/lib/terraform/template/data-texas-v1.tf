# ==============================================================================
# Data

data "terraform_remote_state" "eks" {
  backend = "s3"
  config = {
    key    = var.eks_terraform_state_key
    bucket = var.terraform_platform_state_store
    region = var.aws_region
  }
}

data "terraform_remote_state" "route53" {
  backend = "s3"
  config = {
    key    = var.route53_terraform_state_key
    bucket = var.terraform_platform_state_store
    region = var.aws_region
  }
}

data "terraform_remote_state" "security_groups_k8s" {
  backend = "s3"
  config = {
    key    = var.security_groups_k8s_terraform_state_key
    bucket = var.terraform_platform_state_store
    region = var.aws_region
  }
}

data "terraform_remote_state" "security_groups" {
  backend = "s3"
  config = {
    key    = var.security_groups_terraform_state_key
    bucket = var.terraform_platform_state_store
    region = var.aws_region
  }
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    key    = var.vpc_terraform_state_key
    bucket = var.terraform_platform_state_store
    region = var.aws_region
  }
}

# ==============================================================================
# Terraform state keys and store set by the Make DevOps automation scripts

variable "terraform_platform_state_store" {}

variable "eks_terraform_state_key" {}
variable "route53_terraform_state_key" {}
variable "security_groups_k8s_terraform_state_key" {}
variable "security_groups_terraform_state_key" {}
variable "vpc_terraform_state_key" {}
