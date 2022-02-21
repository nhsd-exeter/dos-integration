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
# # Common
# ############################

variable "route53_terraform_state_key" {
  description = "terraform state key"
}

variable "team_id" {
  description = "team id"
}

# ############################
# API GATEWAY
# ############################

variable "di_endpoint_api_gateway_name" {
  description = "Name for the API Gateway endpoint"
}

variable "di_endpoint_api_gateway_stage" {
  description = "Name for the API Gateway stage"
}


# ############################
# SQS FIFO QUEUE
# ############################

variable "fifo_queue_name" {
  description = "FIFO queue name feed by API Gateway"
}

variable "cr_fifo_queue_name" {
  description = "FIFO queue name fed by event processor"
}

variable "event_processor_lambda_name" {
  description = "Name of event processor lambda"
}

# ############################
# SQS DEAD LETTER QUEUE
# ############################

variable "dead_letter_queue_from_fifo_queue_name" {
  description = ""
}

variable "cr_dead_letter_queue_from_fifo_queue_name" {
  description = ""
}

variable "fifo_dlq_handler_lambda_name" {
  description = ""
}

variable "cr_fifo_dlq_handler_lambda_name" {
  description = ""
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

# ############################
# # SECRETS
# ############################

variable "api_gateway_api_key_name" {
  description = "API Key for DI AWS API Gateway"
}

variable "nhs_uk_api_key_key" {
  description = "API Key key for secrets manager"
}

variable "ip_address_secret" {
  description = "IP Address secret"
}
