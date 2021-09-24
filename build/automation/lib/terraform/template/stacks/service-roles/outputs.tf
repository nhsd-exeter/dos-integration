# ==============================================================================
# Outputs

# --------------------------------------
# admin

output "admin_iam_role_arn" {
  description = "ARN of admin IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.admin_iam_role_arn
}
output "admin_iam_role_name" {
  description = "Name of admin IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.admin_iam_role_name
}

# --------------------------------------
# developer

output "developer_iam_role_arn" {
  description = "ARN of developer IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.developer_iam_role_arn
}
output "developer_iam_role_name" {
  description = "Name of developer IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.developer_iam_role_name
}

# --------------------------------------
# readonly

output "readonly_iam_role_arn" {
  description = "ARN of readonly IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.readonly_iam_role_arn
}
output "readonly_iam_role_name" {
  description = "Name of readonly IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.readonly_iam_role_name
}

# --------------------------------------
# deployment

output "deployment_iam_role_arn" {
  description = "ARN of deployment IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.deployment_iam_role_arn
}
output "deployment_iam_role_name" {
  description = "Name of deployment IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.deployment_iam_role_name
}

# --------------------------------------
# support

output "support_iam_role_arn" {
  description = "ARN of support IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.support_iam_role_arn
}
output "support_iam_role_name" {
  description = "Name of support IAM role"
  value       = module.NAME_TEMPLATE_TO_REPLACE-iam-roles.support_iam_role_name
}
