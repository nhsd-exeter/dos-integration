# ==============================================================================
# Context

locals {
  context = {

    aws_account_id   = var.aws_account_id
    aws_account_name = var.aws_account_name
    aws_region       = var.aws_region
    aws_profile      = var.aws_profile

    org_name             = var.org_name
    programme            = var.programme
    project_group        = var.project_group
    project_group_short  = var.project_group_short
    project_name         = var.project_name
    project_name_short   = var.project_name_short
    project_display_name = var.project_display_name
    project_id           = var.project_id
    project_tag          = var.project_tag
    service_tag          = var.service_tag
    profile              = var.profile
    environment          = var.environment

    tags = {
      Programme   = var.programme
      Project     = var.project_tag
      Service     = var.service_tag
      Profile     = var.profile
      Environment = var.environment
    }

  }
}

# ==============================================================================
# Platform variables set by the Make DevOps automation scripts

variable "aws_account_id" {}
variable "aws_account_name" {}
variable "aws_region" {}
variable "aws_profile" {}

variable "aws_account_id_tools" {}
variable "aws_account_id_nonprod" {}
variable "aws_account_id_prod" {}

variable "aws_role_admin" {}
variable "aws_role_readonly" {}
variable "aws_role_developer" {}
variable "aws_role_support" {}
variable "aws_role_pipeline" {}

variable "texas_tld_name" {}

# ==============================================================================
# Project variables set by the Make DevOps automation scripts

variable "org_name" {}
variable "programme" {}
variable "project_group" {}
variable "project_group_short" {}
variable "project_name" {}
variable "project_name_short" {}
variable "project_display_name" {}
variable "project_id" {}
variable "project_tag" {}
variable "service_tag" {}
variable "profile" {}
variable "environment" {}
