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

variable "terraform_platform_state_store" {
  description = "Texas Platform State store bucket"
}

variable "vpc_terraform_state_key" {
  description = "Texas Platform State store bucket key"
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

# ############################
# # SECURITY GROUP / RULES
# ############################

variable "lambda_security_group_name" {
  description = "Name of the lambda security group"
}

variable "dos_db_name" {
  description = "Name of db dos instance to connect to"
}

# ############################
# # IAM
# ############################

variable "event_processor_role_name" {
  description = "Role name for event processor lambda"
}

variable "orchestrator_role_name" {
  description = "Role name for event processor lambda"
}


variable "event_sender_role_name" {
  description = "Role name for event sender lambda"
}

variable "fifo_dlq_handler_role_name" {
  description = "Role name for fifo dlq handler lambda"
}

variable "cr_fifo_dlq_handler_role_name" {
  description = "Role name for cr_fifo dlq handler lambda"
}

variable "slack_messenger_role_name" {
  description = "Role name for cr_fifo dlq handler lambda"
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

############
# SQS
############
variable "fifo_queue_name" {
  description = ""
}
variable "cr_fifo_queue_name" {
  description = ""
}

variable "dead_letter_queue_from_fifo_queue_name" {
  description = ""
}

variable "cr_dead_letter_queue_from_fifo_queue_name" {
  description = ""
}

# ##############
# # KMS
# ##############

variable "signing_key_alias" {
  description = "Alias of key used for signing"
}

# ######################
# # CLOUDWATCH ALERTS
# #######################
variable "sns_topic_app_alerts_for_slack" {
  description = "The name of the sns topic to recieve alerts for the application to forward to slack"
}
