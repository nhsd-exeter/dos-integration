##########################
# INFRASTRUCTURE COMPONENT
##########################

############
# AWS COMMON
############

variable "aws_profile" {
  description = "The AWS profile"
}

variable "aws_region" {
  description = "The AWS region"
}

variable "aws_account_id" {
  description = "AWS account Number for Athena log location"
}

# ##############
# # TEXAS COMMON
# ##############

variable "profile" {
  description = "The tag used to identify profile e.g. dev, test, live, ..."
}

variable "texas_s3_logs_bucket" {
  description = "The texas s3 log bucket for s3 bucket logs"
}

variable "terraform_platform_state_store" {
  description = "platform state store"
}

variable "vpc_terraform_state_key" {
  description = "vpc state key"
}

# ############################
# # Common
# ############################

variable "route53_terraform_state_key" {
  description = "terraform state key"
}
variable "team_id" {
  description = "team id"
}
variable "programme" {
  description = "programme"
}
variable "environment" {
    description = "environment"
}

# ############################
# # ROUTE53
# ############################


variable "dos_integration_sub_domain_name" {
  type        = string
  description = "sub domain name"
}
variable "texas_hosted_zone" {
  description = "hosted zone"
}

