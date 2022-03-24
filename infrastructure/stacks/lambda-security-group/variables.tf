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
# # SECURITY GROUP / RULES
# ############################

variable "lambda_security_group_name" {
  description = "Name of the lambda security group"
}

variable "dos_db_name" {
  description = "Name of db dos instance to connect to"
}

############
# SNS TOPIC
############

variable "sns_topic_app_alerts_for_slack" {
  description = "The name of the sns topic to recieve alerts for the application to forward to slack"
}
