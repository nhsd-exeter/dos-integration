# ==============================================================================
# Outputs

output "rds_host" {
  description = "The DB instance host name"
  value       = module.NAME_TEMPLATE_TO_REPLACE-rds.db_host
}

output "rds_port" {
  description = "The DB instance port number"
  value       = module.NAME_TEMPLATE_TO_REPLACE-rds.db_port
}

output "rds_name" {
  description = "The DB instance schema name"
  value       = module.NAME_TEMPLATE_TO_REPLACE-rds.db_name
}

output "rds_username" {
  description = "The DB instance username"
  value       = module.NAME_TEMPLATE_TO_REPLACE-rds.db_username
}

output "rds_password" {
  description = "The DB instance password"
  value       = module.NAME_TEMPLATE_TO_REPLACE-rds.db_password
}
