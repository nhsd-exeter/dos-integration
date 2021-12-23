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

variable "service_name" {
  description = "The tag used to identify the service the resource belongs to"
  default     = "uec-dos-int"
}

variable "texas_s3_logs_bucket" {
  description = "The texas s3 log bucket for s3 bucket logs"
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

# ############################
# # SECRETS
# ############################

variable "change_request_username" {
  description = "change request username for DOS API Gateway"
}

variable "change_request_password" {
  description = "change request password for DOS API Gateway"
}
variable "username_key" {
  description = "change request username_key for DOS API Gateway"
}

variable "password_key" {
  description = "change request password_key for DOS API Gateway"
}
variable "change_request_endpoint" {
  description = "change request url endpoint for DOS API Gateway"
}


