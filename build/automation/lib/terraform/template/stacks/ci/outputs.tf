# ==============================================================================
# Outputs

output "ecr_arn_map" {
  description = "Map of repository names to repository ARNs"
  value       = module.NAME_TEMPLATE_TO_REPLACE-ecr.ecr_arn_map
}
output "ecr_id_map" {
  description = "Map of repository names to repository IDs"
  value       = module.NAME_TEMPLATE_TO_REPLACE-ecr.ecr_id_map
}
output "ecr_url_map" {
  description = "Map of repository names to repository URLs"
  value       = module.NAME_TEMPLATE_TO_REPLACE-ecr.ecr_url_map
}
