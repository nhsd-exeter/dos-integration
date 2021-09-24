# ==============================================================================
# User variables

variable "terraform_nhsd_identities_account_id" { description = "NHSD Identities account number" }

variable "terraform_admin_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamAdminRole IAM role"
  default     = ["arn:aws:iam::aws:policy/AdministratorAccess"]
}
variable "terraform_developer_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamDeveloperRole IAM role"
  default     = ["arn:aws:iam::aws:policy/PowerUserAccess"]
}
variable "terraform_readonly_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamReadOnlyRole IAM role"
  default     = ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
}
variable "terraform_deployment_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamDeploymentRole IAM role"
  default     = []
}
variable "terraform_support_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamSupportRole IAM role"
  default     = []
}
