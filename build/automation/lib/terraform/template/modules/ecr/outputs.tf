# ==============================================================================
# Outputs

output "ecr_arn_map" {
  value = zipmap(
    values(aws_ecr_repository.repository)[*].name,
    values(aws_ecr_repository.repository)[*].arn
  )
  description = "Map of repository names to repository ARNs"
}
output "ecr_id_map" {
  value = zipmap(
    values(aws_ecr_repository.repository)[*].name,
    values(aws_ecr_repository.repository)[*].registry_id
  )
  description = "Map of repository names to repository IDs"
}
output "ecr_url_map" {
  value = zipmap(
    values(aws_ecr_repository.repository)[*].name,
    values(aws_ecr_repository.repository)[*].repository_url
  )
  description = "Map of repository names to repository URLs"
}
