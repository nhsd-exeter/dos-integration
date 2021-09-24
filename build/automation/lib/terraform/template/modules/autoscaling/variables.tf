# ==============================================================================
# Mandatory variables

variable "name" { description = "Creates a unique name beginning with the specified prefix" }
variable "lc_name" { description = "" }
variable "asg_name" { description = "" }
variable "health_check_type" { description = "" }
variable "min_size" { description = "" }
variable "max_size" { description = "" }
variable "desired_capacity" { description = "" }
variable "wait_for_capacity_timeout" { description = "" }

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
