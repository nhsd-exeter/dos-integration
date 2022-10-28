# ##############
# # PIPELINE VARIABLES
# ##############

variable "release_pipeline_branch" {
  type        = string
  description = ""
}

variable "pipeline_notification_name" {
  type        = string
  description = ""
}

variable "pipeline_chatbot_channel" {
  type        = string
  description = ""
}

variable "pipeline_topic_name" {
  type        = string
  description = ""
}

variable "github_owner" {
  type        = string
  description = ""
}

variable "github_repo" {
  type        = string
  description = ""
}

variable "service_state_bucket" {
  type        = string
  description = "The S3 bucket used to store the service state"
}

variable "development_pipeline_state" {
  type        = string
  description = "Location of the Terraform state file for the development pipeline"
}
