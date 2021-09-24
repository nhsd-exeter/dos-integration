# ==============================================================================
# Mandatory variables

variable "db_instance" { description = "The DB instance identifier name" }
variable "db_port" { description = "The DB instance port number" }
variable "db_name" { description = "The DB instance schema name" }
variable "db_username" { description = "The DB instance username" }
variable "db_password" { description = "The DB instance password" }

variable "vpc_id" { description = "The VPC network ID" }
variable "subnet_ids" { description = "The list of VPC subnet IDs" }
variable "security_group_ids" { description = "The list of VPC security groups to associate" }

# ==============================================================================
# Default variables

variable "db_max_connections" { default = 10 }
variable "db_instance_class" { default = "db.t3.micro" }
variable "db_allocated_storage" { default = 5 }
variable "db_max_allocated_storage" { default = 50 }
variable "db_backup_retention_period" { default = 0 }
variable "db_multi_az" { default = false }
variable "db_skip_final_snapshot" { default = true }

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
