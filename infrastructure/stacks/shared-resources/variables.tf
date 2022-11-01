# ############################
# API GATEWAY
# ############################

variable "di_endpoint_api_gateway_name" {
  type        = string
  description = "Name for the API Gateway endpoint"
}

variable "di_endpoint_api_gateway_stage" {
  type        = string
  description = "Name for the API Gateway stage"
}

variable "route53_terraform_state_key" {
  type        = string
  description = "terraform state key"
}

# ##############
# # DYNAMO DB
# ##############

variable "change_events_table_name" {
  type        = string
  description = "Name of the table that stores received pharmacy change events"
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

# ##############
# # SQS
# ##############

variable "change_event_queue_name" {
  type        = string
  description = "Change event queue name"
}

variable "shared_resources_dlq" {
  type        = string
  description = "DLQ for change event queue"
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

variable "ip_address_secret" {
  type        = string
  description = "IP Address secret"
}

# ############################
# # ROUTE53
# ############################

variable "dos_integration_sub_domain_name" {
  type        = string
  description = "sub domain name"
}

variable "texas_hosted_zone" {
  type        = string
  description = "hosted zone"
}

# ######################
# # SNS
# #######################

variable "shared_resources_sns_topic_app_alerts_for_slack_default_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the default region"
}

variable "shared_resources_sns_topic_app_alerts_for_slack_route53_health_check_alarm_region" {
  type        = string
  description = "The name of the sns topic to recieve alerts for the application to forward to slack in the route53 health check alarm region"
}

# ##############
# # S3
# ##############

variable "send_email_bucket_name" {
  type        = string
  description = "Name of the bucket to temporarily store emails to be sent"
}

# ##############
# # KINESIS
# ##############

variable "change_event_gateway_subscription_filter_name" {
  type        = string
  description = "Log filter name for change event api gateway logs"
}

variable "dos_integration_firehose" {
  type        = string
  description = "The firehose delivery stream name"
}

variable "di_firehose_role" {
  type        = string
  description = "The firehose delivery stream role name"
}
