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

# ######################
# # CLOUDWATCH DASHBOARD
# #######################
variable "cloudwatch_monitoring_dashboard_name" {
  description = "Name of the dashboard to see the various performance metrics in AWS"
}

variable "dos_db_name" {
  description = "Name of db dos instance to connect to"
}

# ######################
# # CLOUDWATCH ALERTS
# #######################
variable "sqs_dlq_recieved_msg_alert_name" {
  description = "The name of the cloudwatch alert for msgs recieved in the sqs dlq"
}
variable "sns_topic_app_alerts_for_slack" {
  description = "The name of the sns topic to recieve alerts for the application to forward to slack"
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

# ############################
# SQS DEAD LETTER QUEUE
# ############################

variable "dead_letter_queue_from_fifo_queue_name" {
  description = ""
}

variable "cr_dead_letter_queue_from_fifo_queue_name" {
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

# ############################
# # KMS
# ############################
variable "signing_key_alias" {
  description = "Alias of key used for signing"
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


variable "change_request_gateway_subscription_filter_name" {
  description = "Log filter name for change event api gateway logs"
}

variable "fifo_dlq_handler_subscription_filter_name" {
  description = "Log filter name for fifo dlq lambda"
}

variable "cr_fifo_dlq_handler_subscription_filter_name" {
  description = "Log filter name for cr_fifo dlq handler lambda"
}

variable "event_replay_subscription_filter_name" {
  description = "Log filter name for event replay lambda"
}

variable "orchestrator_subscription_filter_name" {
  description = "Log filter name for event replay lambda"
}

variable "dos_integration_firehose" {
  description = "The firehose delivery stream name"
}

variable "firehose_role" {
  description = "The firehose delivery stream role name"
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

variable "fifo_dlq_handler_lambda_name" {
  description = "Name of fifo dlq handler lambda"
}

variable "cr_fifo_dlq_handler_lambda_name" {
  description = "Name of cr_fifo dlq handler lambda"
}

variable "event_replay_lambda_name" {
  description = "Name of event replay lambda"
}

variable "orchestrator_lambda_name" {
  description = "Name of orchestrator lambda"
}
