// Github variables
variable "codestar_connection_arn" {
  type        = string
  description = "You should add Github connection"
}

variable "repository_id" {
  type        = string
  description = "Repository ID of the project ex: AbdellatifSfeir/sam-app"
}

variable "branch_name" {
  type    = string
  default = "develop"
}

// Lambda informations
variable "prefix" {
  type = string
}

variable "cloudformation_stack_name" {
  type = string
  description = "The name of the cloudformation project created by sam"
}