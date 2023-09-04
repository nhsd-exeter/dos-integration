# ############################
# API GATEWAY
# ############################

variable "di_endpoint_api_gateway_name" {
  type        = string
  description = "Name for the API Gateway endpoint"
}

# ##############
# # SNS
# ##############

variable "shared_resources_sns_topic_app_alerts_for_slack_default_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the default region (shared resources)"
}

variable "shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the route53 health check alarm region (shared resources)"
}

# ##############
# # PARAMETER STORE
# ##############

variable "blue_green_deployment_previous_version_parameter_name" {
  type        = string
  description = "The name of the parameter in the parameter store that stores the previous version of the blue/green deployment"
}

variable "blue_green_deployment_current_version_parameter_name" {
  type        = string
  description = "The name of the parameter in the parameter store that stores the current version of the blue/green deployment"
}

variable "previous_blue_green_environment" {
  type        = string
  description = "(optional) The name of the previous blue/green environment"
  default     = "NA"
}

# ######################
# # CLOUDWATCH DASHBOARD
# #######################

variable "cloudwatch_monitoring_dashboard_name" {
  type        = string
  description = "Name of the dashboard to see the various performance metrics in AWS"
}

variable "cloudwatch_data_dashboard_name" {
  type        = string
  description = "Name of the dashboard to see the various data metrics in AWS"
}

variable "dos_db_cluster_name" {
  type        = string
  description = "Name of db dos cluster to connect to"
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
  description = "DLQ for chane event queue"
}

variable "holding_queue_dlq" {
  type        = string
  description = "DLQ for holding queue"
}

variable "update_request_dlq" {
  type        = string
  description = "DLQ for update request queue"
}
