# ==============================================================================
# Mandatory variables

variable "table_name" { description = "The DynamoDB table name" }
variable "hash_key" { description = "The DynamoDB table hash key" }
variable "attributes" { description = "The DynamoDB table attributes" }

# ==============================================================================
# Default variables

# variable "range_key" { default = null }
# variable "billing_mode" { default = null }
# variable "read_capacity" { default = null }
# variable "write_capacity" { default = null }


# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
