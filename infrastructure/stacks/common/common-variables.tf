##########################
# INFRASTRUCTURE COMPONENT
##########################

############
# AWS COMMON
############

variable "aws_region" {
  type        = string
  description = "The default AWS region"
}

variable "route53_health_check_alarm_region" {
  type        = string
  description = "The AWS region for the CloudWatch global alarms"
}

variable "aws_account_name" {
  type        = string
  description = "Current AWS account name"
}

variable "aws_account_id" {
  type        = number
  description = "Current AWS account ID"
}

variable "aws_account_id_nonprod" {
  type        = number
  description = "Account ID for the nonprod account"
}

variable "aws_account_id_mgmt" {
  type        = number
  description = "Account ID for the management account"
}

variable "aws_account_id_prod" {
  type        = number
  description = "Account ID for the production account"
}

variable "aws_account_id_identities" {
  type        = number
  description = "Account ID for the Identities account"
}

variable "aws_account_id_live_parent" {
  type        = number
  description = "Account ID for the live parent account"
}

variable "aws_account_id_tools" {
  type        = number
  description = "Account ID for the tools account"
  default     = "00000000000"
}


# ##############
# # TEXAS COMMON
# ##############

variable "profile" {
  type        = string
  description = "The tag used to identify profile e.g. dev, test, live, ..."
}

variable "programme" {
  type        = string
  description = "Programme name"
}

variable "project_id" {
  type        = string
  description = "Project ID"
}

variable "environment" {
  type        = string
  description = "Environment name (don't use if application stack)"
}

variable "shared_environment" {
  type        = string
  description = "Environment name of the shared resources"
}

variable "blue_green_environment" {
  type        = string
  description = "Environment name of the blue/green resources"
}

variable "project_display_name" {
  type        = string
  description = "Project display name"
}

variable "terraform_platform_state_store" {
  type        = string
  description = "Texas Platform State store bucket"
  default     = ""
}

# ################
# # TAGGING COMMON
# ################

variable "data_classification" {
  type        = string
  description = "Project data classification"
  default     = "Worry if you see this message in Prod"
}

variable "service_category" {
  type        = string
  description = "Project service category"
  default     = "Worry if you see this message in Prod"
}

variable "distribution_list" {
  type        = string
  description = "Project distribution list"
  default     = "Worry if you see this message in Prod"
}
