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

# ######################
# # CLOUDWATCH DASHBOARD
# #######################
variable "cloudwatch_monitoring_dashboard_name" {
  description = "Name of the dashboard to see the various performance metrics in AWS"
}

variable "dos_db_name" {
  description = "Name of db dos instance to connect to"
}

variable "fifo_queue_name" {
  description = "FIFO queue name feed by API Gateway"
}

variable "event_processor_lambda_name" {
  description = "Name of event processor lambda"
}

variable "event_sender_lambda_name" {
  description = "Name of event sender lambda"
}
variable "fifo_dlq_handler_lambda_name" {
  description = "Fifo DLQ Handler"
}
variable "dead_letter_queue_from_fifo_queue_name" {
  description = "FIFO dead letter queue name"
}

variable "eventbridge_dlq_handler_lambda_name" {
  description = "Event bridge dlq handler"
}

variable "di_endpoint_api_gateway_name" {
  description = "Endpoint consumed by NHS UK"
}

variable "change_request_receiver_api_name" {
  description = "Name for the API Gateway endpoint on request receiver side"
}

variable "eventbridge_bus_name" {
  description = "Name of the eventbridge event bus"
}

variable "dead_letter_queue_from_event_bus_name" {
  description = "Name of the eventbridge dead letter queue"
}

variable "change_request_eventbridge_rule_name" {
  description = "Rule to pickup change request from eventbridge bus"
}
