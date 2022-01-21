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
# # EVENTBRIDGE
# ############################

variable "eventbridge_bus_name" {
  description = "Name of the eventbridge event bus"
}

variable "change_request_eventbridge_rule_name" {
  description = "Rule to pickup change request from eventbridge bus"
}

variable "dos_api_gateway_eventbridge_connection_name" {
  description = "Connection name for connection details for DoS API Gateway"
}

variable "dos_api_gateway_api_destination_name" {
  description = "Name for API Destination for DoS API Gateway"
}

variable "dos_api_gateway_api_destination_url" {
  description = "URL for API Destination for DoS API Gateway"
}

variable "change_request_receiver_api_key_name" {
  description = ""
}

variable "change_request_receiver_api_key_key" {
  description = ""
}

variable "eventbridge_target_role_name" {
  description = "Name of the eventbridge target role"
}

variable "eventbridge_target_policy_name" {
  description = "Name of the eventbridge target policy"
}

# ############################
# EVENTBRIDGE DEAD LETTER QUEUE
# ############################

variable "dead_letter_queue_from_event_bus_name" {
  description = ""
}

# ############################
# # LAMBDA
# ############################

variable "event_processor_lambda_name" {
  description = "Name of event processor lambda"
}
