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
  description = "Texas Platform State store bucket"
}

variable "vpc_terraform_state_key" {
  description = "Texas Platform State store bucket key"
}

variable "route53_terraform_state_key" {
  description = "terraform state key"
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

# ##############
# # DYNAMO DB
# ##############
variable "change_events_table_name" {
  description = "Name of the table that stores received pharmacy change events"
}

variable "signing_key_alias" {
  description = "Alias of key used for signing"
}
