# ##############
# # PIPELINE VARIABLES
# ##############

variable "release_pipeline_branch" {
  description = ""
}
variable "pipeline_notification_name" {
  description = ""
}

variable "pipeline_chatbot_channel" {
  description = ""
}

variable "pipeline_topic_name" {
  description = ""
}

variable "github_owner" {
  description = ""
}

variable "github_repo" {
  description = ""
}

variable "service_state_bucket" {
  description = "The S3 bucket used to store the service state"
}

variable "development_pipeline_state" {
  description = "Location of the Terraform state file for the development pipeline"
}
