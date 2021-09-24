# ==============================================================================
# Mandatory variables

variable "vpc_name" { description = "The VPC network name" }

# ==============================================================================
# Default variables

variable "vpc_id" {
  description = "The VPC network ID used to define the CIDR address block, i.e. 10.vpc_id.0.0/16"
  default     = 0
}
variable "public_subnet_port_rules" {
  description = "The list of public subnet ports to be accessible from the internet as a `rule_no = port` pair"
  default = {
    101 = 80
    102 = 443
  }
}
variable "private_subnet_port_rules" {
  description = "The list of private subnet ports to be accessible from the public subnet as a `rule_no = port` pair"
  default = {
    101 = 443
  }
}
variable "internal_subnet_port_rules" {
  description = "The list of internal subnet ports to be accessible from the private subnet as a `rule_no = port` pair"
  default = {
    101 = 443
  }
}

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
