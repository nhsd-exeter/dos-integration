############
# VPC
############

variable "vpc_terraform_state_key" {
  type        = string
  description = "Texas Platform State store bucket key"
}

# ############################
# # SECRETS
# ############################

variable "api_gateway_api_key_name" {
  type        = string
  description = "API Key for DI AWS API Gateway"
}

variable "nhs_uk_api_key_key" {
  type        = string
  description = "API Key key for secrets manager"
}

# ############################
# # SECURITY GROUP / RULES
# ############################

variable "lambda_security_group_name" {
  type        = string
  description = "Name of the lambda security group"
}

variable "dos_db_name" {
  type        = string
  description = "Name of db dos instance to connect to"
}

variable "dos_db_replica_name" {
  type        = string
  description = "Name of db dos read replica instance to connect to"
}

# ############################
# # IAM
# ############################
variable "orchestrator_role_name" {
  type        = string
  description = "Role name for event processor lambda"
}

variable "change_event_dlq_handler_role_name" {
  type        = string
  description = "Role name for change event dlq handler lambda"
}

variable "dos_db_update_dlq_handler_role_name" {
  type        = string
  description = "Role name for dos db update dlq handler lambda"
}

variable "slack_messenger_role_name" {
  type        = string
  description = "Role name for slack messenger dlq handler lambda"
}

variable "event_replay_role_name" {
  type        = string
  description = "Role name for event replay lambda"
}

variable "dos_db_handler_role_name" {
  type        = string
  description = "Role name for dos db handler lambda"
}

variable "send_email_role_name" {
  type        = string
  description = "Role name for send email lambda"
}

variable "ingest_change_event_role_name" {
  type        = string
  description = "Role name for ingest change event lambda"
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

variable "send_email_lambda_name" {
  type        = string
  description = "Name of send email lambda"
}

variable "ingest_change_event_lambda_name" {
  type        = string
  description = "Name of ingest change event lambda"
}

# ##############
# # DYNAMO DB
# ##############

variable "change_events_table_name" {
  type        = string
  description = "Name of the table that stores received pharmacy change events"
}

############
# SQS
############

variable "change_event_queue_name" {
  type        = string
  description = "Change event SQS name"
}

variable "update_request_queue_name" {
  type        = string
  description = "Update request SQS name"
}

variable "holding_queue_name" {
  type        = string
  description = "Holding queue SQS name"
}

variable "change_event_dlq" {
  type        = string
  description = "Change event SQS DLQ name"
}

variable "update_request_dlq" {
  type        = string
  description = "Update request SQS DLQ name"
}

# ##############
# # KMS
# ##############

variable "signing_key_alias" {
  type        = string
  description = "Alias of key used for signing in the default region"
}

variable "route53_health_check_alarm_region_signing_key_alias" {
  type        = string
  description = "Alias of key used for signing in the alarm region"
}

variable "developer_role_name" {
  type        = string
  description = "Role name of developer's role so that it can access the KMS key for the dbcloner"
}

# ######################
# # CLOUDWATCH ALERTS
# #######################

variable "sns_topic_app_alerts_for_slack_default_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the default region"
}

variable "sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the alarm region"
}

# ##############
# # S3
# ##############

variable "send_email_bucket_name" {
  type        = string
  description = "Name of the bucket to temporarily store emails to be sent"
}
