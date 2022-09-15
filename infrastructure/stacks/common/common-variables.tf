##########################
# INFRASTRUCTURE COMPONENT
##########################

############
# AWS COMMON
############

variable "aws_region" {
  description = "The AWS region"
}

variable "aws_account_name" {
  description = "Current AWS account name"
}

variable "aws_account_id" {
  description = "Current AWS account ID"
}

variable "aws_account_id_nonprod" {
  description = "Account ID for the nonprod account"
}

variable "aws_account_id_mgmt" {
  description = "Account ID for the management account"
}

variable "aws_account_id_prod" {
  description = "Account ID for the production account"
}

variable "aws_account_id_identities" {
  description = "Account ID for the Identities account"
}

variable "aws_account_id_live_parent" {
  description = "Account ID for the live parent account"
}

variable "aws_account_id_tools" {
  description = "Account ID for the tools account"
  default     = "00000000000"
}
# ##############
# # TEXAS COMMON
# ##############

variable "profile" {
  description = "The tag used to identify profile e.g. dev, test, live, ..."
}

variable "programme" {
  description = "Programme name"
}

variable "project_id" {
  description = "Project ID"
}

variable "environment" {
  description = "Environment name"
}

variable "project_display_name" {
  type        = string
  description = "Project display name"
}

variable "terraform_platform_state_store" {
  description = "Texas Platform State store bucket"
}
