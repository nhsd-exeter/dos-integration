# ##############
# # LAMBDA
# ##############

variable "ingest_change_event_lambda_name" {
  type        = string
  description = "Name of ingest change event lambda"
}

variable "slack_messenger_lambda_name" {
  type        = string
  description = "Name of slack messenger lambda"
}

# ##############
# # SQS
# ##############

variable "change_event_queue_name" {
  type        = string
  description = "Change event queue name"
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
