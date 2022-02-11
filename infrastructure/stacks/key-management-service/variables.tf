################
#  AWS COMMON  #
################

variable "aws_profile" {
  description = "The AWS profile"
}

variable "aws_account_id" {
  description = "AWS account Number for Athena log location"
}

variable "aws_region" {
  description = "The AWS region"
}

##################
#  TEXAS COMMON  #
##################

variable "profile" {
  description = "The tag used to identify profile e.g. dev, test, live, ..."
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

############################
#  Key Management Service  #
############################

variable "kms_managed_key_alias" {
  description = "The alias for the customer managed key"
}