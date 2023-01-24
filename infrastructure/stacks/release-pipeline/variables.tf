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
