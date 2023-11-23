# ##############
# # General
# ##############

variable "docker_registry" {
  type        = string
  description = "Docker registry"
}

variable "project_deployment_secrets" {
  type        = string
  description = "Name of the project deployment secrets"
}

############
# VPC
############

variable "aws_vpc_name" {
  type        = string
  description = "Name of the VPC"
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

variable "db_writer_sg_name" {
  type        = string
  description = "Name of db dos writer security group to connect to"
}

variable "db_reader_sg_name" {
  type        = string
  description = "Name of db dos reader security group to connect to"
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

variable "change_event_queue" {
  type        = string
  description = "Change event SQS name"
}

variable "update_request_queue" {
  type        = string
  description = "Update request SQS name"
}

variable "holding_queue" {
  type        = string
  description = "Holding queue SQS name"
}

# ############################
# SQS DEAD LETTER QUEUE
# ############################

variable "change_event_dlq" {
  type        = string
  description = "Change event SQS DLQ name"
}

variable "holding_queue_dlq" {
  type        = string
  description = "DLQ for holding queue"
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

variable "developer_role" {
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

# ##############
# # FIREHOSE
# ##############

variable "service_matcher_subscription_filter_name" {
  type        = string
  description = "Log filter name for event processor lambda"
}

variable "service_sync_dos_subscription_filter_name" {
  type        = string
  description = "Log filter name for event sender lambda"
}

variable "service_sync_di_subscription_filter_name" {
  type        = string
  description = "Log filter name for event sender lambda"
}

variable "change_event_dlq_handler_subscription_filter_name" {
  type        = string
  description = "Log filter name for fifo dlq lambda"
}

variable "dos_db_update_dlq_handler_subscription_filter_name" {
  type        = string
  description = "Log filter name for cr_fifo dlq handler lambda"
}

variable "event_replay_subscription_filter_name" {
  type        = string
  description = "Log filter name for event replay lambda"
}

variable "slack_messenger_subscription_filter_name" {
  type        = string
  description = "Log filter name for slack messenger lambda"
}


variable "send_email_subscription_filter_name" {
  type = string

  description = "Log filter name for send email lambda"
}

variable "ingest_change_event_subscription_filter_name" {
  type        = string
  description = "Log filter name for ingest change event lambda"
}

variable "quality_checker_subscription_filter_name" {
  type        = string
  description = "Log filter name for quality checker lambda"
}

variable "dos_integration_firehose" {
  type        = string
  description = "The firehose delivery stream name"
}

variable "dos_firehose" {
  type        = string
  description = "The firehose delivery stream name"
}

variable "di_firehose_role" {
  type        = string
  description = "The firehose delivery stream role name"
}

variable "dos_firehose_role" {
  type        = string
  description = "The firehose delivery stream role name"
}

# ############################
# # LAMBDA NAMES
# ############################

variable "change_event_dlq_handler_lambda" {
  type        = string
  description = "Name of change event dlq handler lambda"
}

variable "dos_db_update_dlq_handler_lambda" {
  type        = string
  description = "Name of dos db update dlq handler lambda"
}

variable "dos_db_handler_lambda" {
  type        = string
  description = "Name of dos db handler lambda"
}

variable "event_replay_lambda" {
  type        = string
  description = "Name of event replay lambda"
}

variable "ingest_change_event_lambda" {
  type        = string
  description = "Name of ingest change event lambda"
}

variable "send_email_lambda" {
  type        = string
  description = "Name of send email lambda"
}

variable "service_matcher_lambda" {
  type        = string
  description = "Name of event processor lambda"
}

variable "service_sync_lambda" {
  type        = string
  description = "Name of event sender lambda"
}

variable "slack_messenger_lambda" {
  type        = string
  description = "Name of slack messenger lambda"
}

variable "quality_checker_lambda" {
  type        = string
  description = "Name of quality checker lambda"
}

# ##############
# # Docker Image Names
# ##############

variable "change_event_dlq_handler" {
  type        = string
  description = "Name of change event dlq handler docker image"
}

variable "dos_db_handler" {
  type        = string
  description = "Name of dos db handler docker image"
}

variable "dos_db_update_dlq_handler" {
  type        = string
  description = "Name of dos db update dlq handler docker image"
}

variable "event_replay" {
  type        = string
  description = "Name of event replay docker image"
}

variable "ingest_change_event" {
  type        = string
  description = "Name of ingest change event docker image"
}

variable "send_email" {
  type        = string
  description = "Name of send email docker image"
}

variable "service_matcher" {
  type        = string
  description = "Name of event processor docker image"
}

variable "service_sync" {
  type        = string
  description = "Name of event sender docker image"
}

variable "slack_messenger" {
  type        = string
  description = "Name of slack messenger docker image"
}

variable "quality_checker" {
  type        = string
  description = "Name of quality checker docker image"
}


# ##############
# # LAMBDA VERSIONS
# ##############

variable "change_event_dlq_handler_version" {
  type        = string
  description = "Version of change event dlq handler docker image"
}

variable "dos_db_handler_version" {
  type        = string
  description = "Version of dos db handler docker image"
}

variable "dos_db_update_dlq_handler_version" {
  type        = string
  description = "Version of dos db update dlq handler docker image"
}

variable "event_replay_version" {
  type        = string
  description = "Version of event replay docker image"
}

variable "ingest_change_event_version" {
  type        = string
  description = "Version of ingest change event docker image"
}

variable "send_email_version" {
  type        = string
  description = "Version of send email docker image"
}

variable "service_matcher_version" {
  type        = string
  description = "Version of event processor docker image"
}

variable "service_sync_version" {
  type        = string
  description = "Version of event sender docker image"
}

variable "slack_messenger_version" {
  type        = string
  description = "Version of slack messenger docker image"
}

variable "quality_checker_version" {
  type        = string
  description = "Version of quality checker docker image"
}

# ##############
# # LAMBDA CONFIG
# ##############

variable "service_matcher_max_concurrency" {
  type        = string
  description = "The maximum number of concurrent executions you want to reserve for the function."
}

variable "service_sync_max_concurrency" {
  type        = string
  description = "The maximum number of concurrent executions you want to reserve for the function."
}

# ##############
# # LAMBDA ENVIRONMENT VARIABLES
# ##############

variable "lambda_powertools_service_name" {
  type        = string
  description = "AWS Lambda Powertools Service name for lambda function logging"
}

variable "log_level" {
  type        = string
  description = "Log level for lambda functions"
}

variable "dos_db_reader_name" {
  type        = string
  description = "Name of the dos db reader"
  default     = ""
}

variable "dos_db_writer_route_53" {
  type        = string
  description = "Route 53 name of the dos db writer"
  default     = ""
}

variable "dos_db_reader_route_53" {
  type        = string
  description = "Route 53 name of the dos db reader"
  default     = ""
}

variable "dos_db_port" {
  type        = string
  description = "Port of the dos db"
  default     = ""
}

variable "dos_db_name" {
  type        = string
  description = "Name of the dos db"
  default     = ""
}

variable "dos_db_schema" {
  type        = string
  description = "Schema of the dos db"
  default     = ""
}

variable "dos_db_writer_security_group_name" {
  type        = string
  description = "Name of the dos db writer security group"
  default     = ""
}

variable "dos_db_reader_security_group_name" {
  type        = string
  description = "Name of the dos db reader security group"
  default     = ""
}

variable "dos_db_writer_secret_name" {
  type        = string
  description = "Name of the dos db writer secret"
  default     = ""
}

variable "dos_db_writer_secret_key" {
  type        = string
  description = "Key of the dos db writer secret"
  default     = ""
}

variable "dos_db_reader_secret_name" {
  type        = string
  description = "Name of the dos db reader secret"
  default     = ""
}

variable "dos_db_reader_secret_key" {
  type        = string
  description = "Key of the dos db reader secret"
  default     = ""
}

variable "slack_alert_channel" {
  type        = string
  description = "The slack channel to send alerts to"
  default     = ""
}

variable "dos_db_read_only_user_name_secret_key" {
  type        = string
  description = "Key of the dos db read only user name secret"
}

variable "odscode_starting_character" {
  type        = string
  description = "The starting character of the ods code"
}
