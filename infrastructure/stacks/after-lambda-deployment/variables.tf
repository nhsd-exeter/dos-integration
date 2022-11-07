# ############################
# API GATEWAY
# ############################

variable "di_endpoint_api_gateway_name" {
  type        = string
  description = "Name for the API Gateway endpoint"
}

# ######################
# # CLOUDWATCH DASHBOARD
# #######################

variable "cloudwatch_monitoring_dashboard_name" {
  type        = string
  description = "Name of the dashboard to see the various performance metrics in AWS"
}

variable "dos_db_name" {
  type        = string
  description = "Name of db dos instance to connect to"
}

variable "dos_db_replica_name" {
  type        = string
  description = "Name of db dos replica to connect to"
}

# ######################
# # CLOUDWATCH ALERTS
# #######################

variable "sqs_dlq_recieved_msg_alert_name" {
  type        = string
  description = "The name of the cloudwatch alert for msgs recieved in the sqs dlq"
}

variable "sns_topic_app_alerts_for_slack_default_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the default region"
}

variable "sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the route53 health check alarm region"
}

# ############################
# SQS FIFO QUEUE
# ############################

variable "change_event_queue_name" {
  type        = string
  description = "Change event queue name"
}

variable "holding_queue_name" {
  type        = string
  description = "Holding queue name"
}

variable "update_request_queue_name" {
  type        = string
  description = "Update request queue name"
}

# ############################
# SQS DEAD LETTER QUEUE
# ############################

variable "change_event_dlq" {
  type        = string
  description = "DLQ for change event queue (when connected to blue/green environment) and holding queue"
}

variable "update_request_dlq" {
  type        = string
  description = "DLQ for update request queue"
}

# ############################
# # KMS
# ############################

variable "signing_key_alias" {
  type        = string
  description = "Alias of key used for signing in the default region"
}

variable "route53_health_check_alarm_region_signing_key_alias" {
  type        = string
  description = "Alias of key used for signing in the route53 health check alarm region"
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

variable "orchestrator_subscription_filter_name" {
  type        = string
  description = "Log filter name for orchestrator lambda"
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
# ##############
# # LAMBDAS
# ##############

variable "service_matcher_lambda_name" {
  type        = string
  description = "Name of event processor lambda"
}

variable "service_sync_lambda_name" {
  type        = string
  description = "Name of event sender lambda"
}

variable "change_event_dlq_handler_lambda_name" {
  type        = string
  description = "Name of fifo dlq handler lambda"
}

variable "dos_db_update_dlq_handler_lambda_name" {
  type        = string
  description = "Name of cr_fifo dlq handler lambda"
}

variable "event_replay_lambda_name" {
  type        = string
  description = "Name of event replay lambda"
}

variable "orchestrator_lambda_name" {
  type        = string
  description = "Name of orchestrator lambda"
}

variable "slack_messenger_lambda_name" {
  type        = string
  description = "Name of slack messenger lambda"
}

variable "send_email_lambda_name" {
  type        = string
  description = "Name of send email lambda"
}

variable "ingest_change_event_lambda_name" {
  type        = string
  description = "Name of ingest change event lambda"
}
