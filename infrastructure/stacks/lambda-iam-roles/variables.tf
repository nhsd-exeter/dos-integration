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
# # IAM
# ############################

variable "event_processor_role_name" {
  description = "Role name for event processor lambda"
}

variable "event_sender_role_name" {
  description = "Role name for event sender lambda"
}

variable "fifo_dlq_handler_role_name" {
  description = "Role name for fifo dlq handler lambda"
}

variable "eventbridge_dlq_handler_role_name" {
  description = "Role name for eventbridge dlq handler lambda"
}

variable "event_replay_role_name" {
  description = "Role name for event replay lambda"
}

variable "test_db_checker_handler_role_name" {
  description = "Role name for test db checker handler lambda"
}

# ##############
# # DYNAMO DB
# ##############
variable "change_events_table_name" {
  description = "Name of the table that stores received pharmacy change events"
}


# ##############
# # KMS
# ##############

variable "ddb_kms_key_alias" {
  description = "Key alias for the ddb kms key"
}

variable "signing_key_alias" {
  description = "Alias of key used for signing"
}

variable "sqs_kms_key_alias" {
  description = "Key alias for the sqs kms key"
}


############
# SQS
############
variable "fifo_queue_name" {
  description = ""
}

variable "dead_letter_queue_from_fifo_queue_name" {
  description = ""
}

variable "dead_letter_queue_from_event_bus_name" {
  description = ""
}
