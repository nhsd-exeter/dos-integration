# ==============================================================================
# Mandatory variables

variable "name" { description = "Creates a unique name beginning with the specified prefix" }

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
