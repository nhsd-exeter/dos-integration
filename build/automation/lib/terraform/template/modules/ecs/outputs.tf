# ==============================================================================
# Outputs

output "this_ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs.this_ecs_cluster_arn
}
output "this_ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = module.ecs.this_ecs_cluster_id
}
output "this_ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.this_ecs_cluster_name
}
