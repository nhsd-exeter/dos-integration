##########################
# INFRASTRUCTURE COMPONENT
##########################

############
# AWS COMMON
############

variable "aws_region" {
  description = "The AWS region"
}

variable "aws_account_id" {
  description = "AWS account Number for Athena log location"
}

variable "aws_account_id_nonprod" {
  description = ""
}

variable "aws_account_id_mgmt" {
  description = ""
}

variable "aws_account_id_prod" {
  description = ""
}

variable "aws_account_id_identities" {
  description = ""
}

variable "aws_vpc_name" {
  description = ""
}


variable "aws_account_id_live_parent" {
  description = ""
}

# ##############
# # TEXAS COMMON
# ##############

variable "pipeline_notification_name" {
  description = ""
}

variable "pipeline_chatbot_channel" {
  description = ""
}

variable "pipeline_topic_name" {
  description = ""
}

variable "github_owner" {
  description = ""
}

variable "github_repo" {
  description = ""
}

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

variable "from_release_branch" {
  description = "This is from a release branch"
  type        = bool
  default     = false
}

variable "service_state_bucket" {
  description = "The S3 bucket used to store the service state"
}

variable "development_pipeline_state" {
  description = "Location of the Terraform state file for the development pipeline"
}
