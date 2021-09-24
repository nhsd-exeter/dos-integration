# ==============================================================================
# Outputs

output "db_host" {
  description = "The DB instance host name"
  value       = module.rds.this_db_instance_address
}
output "db_port" {
  description = "The DB instance port number"
  value       = module.rds.this_db_instance_port
}
output "db_name" {
  description = "The DB instance schema name"
  value       = module.rds.this_db_instance_name
}
output "db_username" {
  description = "The DB instance username"
  value       = module.rds.this_db_instance_username
}
output "db_password" {
  description = "The DB instance password"
  value       = module.rds.this_db_instance_password
}
