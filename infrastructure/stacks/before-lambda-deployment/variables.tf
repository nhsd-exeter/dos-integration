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

variable "dos_db_replica_name" {
  description = "Name of db dos read replica instance to connect to"
}

# ############################
# # IAM
# ############################

variable "service_matcher_role_name" {
  description = "Role name for event processor lambda"
}

variable "orchestrator_role_name" {
  description = "Role name for event processor lambda"
}

variable "service_sync_role_name" {
  description = "Role name for event sender lambda"
}

variable "change_event_dlq_handler_role_name" {
  description = "Role name for change event dlq handler lambda"
}

variable "dos_db_update_dlq_handler_role_name" {
  description = "Role name for dos db update dlq handler lambda"
}

variable "slack_messenger_role_name" {
  description = "Role name for slack messenger dlq handler lambda"
}

variable "event_replay_role_name" {
  description = "Role name for event replay lambda"
}

variable "dos_db_handler_role_name" {
  description = "Role name for dos db handler lambda"
}

# ##############
# # LAMBDAS
# ##############

variable "service_matcher_lambda_name" {
  type        = string
  description = "Name of service matcher lambda"
}

variable "service_sync_lambda_name" {
  type        = string
  description = "Name of service sync lambda"
}

variable "change_event_dlq_handler_lambda_name" {
  type        = string
  description = "Name of change event dlq handler lambda"
}

variable "dos_db_update_dlq_handler_lambda_name" {
  type        = string
  description = "Name of dos db update dlq handler lambda"
}

variable "dos_db_handler_lambda_name" {
  type        = string
  description = "Name of dos db handler lambda"
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
variable "change_event_queue_name" {
  description = ""
}
variable "update_request_queue_name" {
  description = ""
}

variable "change_event_dlq" {
  description = ""
}

variable "update_request_dlq" {
  description = ""
}

# ##############
# # KMS
# ##############

variable "signing_key_alias" {
  description = "Alias of key used for signing"
}

variable "developer_role_name" {
  description = "Role name of developer's role so that it can access the KMS key for the dbcloner"
}

# ######################
# # CLOUDWATCH ALERTS
# #######################
variable "sns_topic_app_alerts_for_slack" {
  description = "The name of the sns topic to recieve alerts for the application to forward to slack"
}
