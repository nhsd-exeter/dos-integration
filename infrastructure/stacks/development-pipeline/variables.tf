# ##############
# # PIPELINE VARIABLES
# ##############
variable "code_pipeline_branch_name" {
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
variable "mgmt_vpc_name" {
  type        = string
  description = "Name of the management VPC"
}
