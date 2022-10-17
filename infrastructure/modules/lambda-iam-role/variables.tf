variable "lambda_name" {
  description = "The name of the lambda function"
}

variable "use_custom_policy" {
  description = "Use custom policy"
  type        = bool
  default     = false
}

variable "custom_lambda_policy" {
  description = "The custom policy for the lambda function"
}
