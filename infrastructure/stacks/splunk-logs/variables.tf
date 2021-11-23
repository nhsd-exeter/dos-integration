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

# ##############
# # FIREHOSE
# ##############

variable "event_receiver_subscription_filter_name" {
  description = ""
}

variable "event_processor_subscription_filter_name" {
  description = ""
}

variable "event_sender_subscription_filter_name" {
  description = ""
}

variable "dos_integration_firehose" {
  description = "The firehose delivery stream name"
}

variable "firehose_role" {
  description = "The firehose delivery stream role arn"
}

# ##############
# # LAMBDA
# ##############

variable "event_receiver_lambda_name" {
  description = ""
}

variable "event_processor_lambda_name" {
  description = ""
}

variable "event_sender_lambda_name" {
  description = ""
}
