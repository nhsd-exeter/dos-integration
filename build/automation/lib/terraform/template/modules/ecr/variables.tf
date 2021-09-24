# ==============================================================================
# Mandatory variables

variable "names" { description = "The names of the ECR repositories" }

# ==============================================================================
# Default variables

variable "image_tag_mutability" { default = "MUTABLE" }
variable "encryption_configuration" { default = { encryption_type = "AES256", kms_key = null } }
variable "scan_on_push" { default = true }
variable "protected_tags" { default = [] }
variable "max_image_count" { default = 333 }
variable "principals_readonly_access" { default = [] }
variable "principals_full_access" { default = [] }
variable "principals_dont_deny_delete" { default = [] }

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
