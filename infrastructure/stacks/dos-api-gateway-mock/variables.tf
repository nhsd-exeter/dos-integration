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

variable "texas_s3_logs_bucket" {
  description = "The texas s3 log bucket for s3 bucket logs"
}

variable "terraform_platform_state_store" {
  description = "Texas Platform State store bucket"
}

variable "vpc_terraform_state_key" {
  description = "Texas Platform State store bucket key"
}

variable "route53_terraform_state_key" {
  description = "terraform state key"
}

# ##############
# # API GATEWAY
# ##############

variable "dos_api_gateway_name" {
  description = "The stage of the api gateway"
}

variable "dos_api_gateway_stage" {
  description = "The stage of the api gateway"
}

variable "dos_api_gateway_authoriser" {
  description = "The stage of the api gateway"
}

variable "event_sender_role_name" {
  description = "Name of the event sender lambda role"
}

variable "dos_api_gateway_secret" {
  description = "The secrets for the api gateway"
}

variable "dos_api_gateway_secret_username_key" {
  description = ""
}

variable "dos_api_gateway_secret_password_key" {
  description = ""
}

# ##############
# # LAMBDAS
# ##############

variable "authoriser_lambda_name" {
  description = "The authoriser lambda name"
}
variable "image_version" {
  description = "The image version"
}

variable "aws_same_account_docker_registry" {
  description = "ECR repository for authoriser lambda"
}

variable "dos_api_gateway_lambda_name" {
  description = "The authoriser lambda name"
}

# ############################
# # ROUTE53
# ############################

variable "texas_hosted_zone" {
  description = "hosted zone"
}
