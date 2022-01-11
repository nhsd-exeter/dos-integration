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

# ##############
# # FIREHOSE
# ##############

variable "event_processor_subscription_filter_name" {
  description = "Log filter name for event processor lambda"
}

variable "event_sender_subscription_filter_name" {
  description = "Log filter name for event sender lambda"
}

variable "change_event_gateway_subscription_filter_name" {
  description = "Log filter name for change event api gateway logs"
}

variable "dos_integration_firehose" {
  description = "The firehose delivery stream name"
}
variable "di_endpoint_api_gateway_name" {
  description = "DI Endpoint"
}

variable "firehose_role" {
  description = "The firehose delivery stream role name"
}
variable "di_endpoint_api_gateway_stage" {
  description = ""
}
# ##############
# # LAMBDA
# ##############

variable "event_processor_lambda_name" {
  description = "Name of event processor lambda"
}

variable "event_sender_lambda_name" {
  description = "Name of event sender lambda"
}
