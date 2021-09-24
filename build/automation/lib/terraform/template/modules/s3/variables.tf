# ==============================================================================
# Mandatory variables

variable "bucket_name" { description = "The S3 bucket name" }

# ==============================================================================
# Default variables

variable "attach_policy" { default = false }
variable "policy" { default = null }

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
