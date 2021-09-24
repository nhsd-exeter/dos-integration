# ==============================================================================
# Mandatory variables

variable "nhsd_identities_account_id" { description = "NHSD Identities account number" }

# ==============================================================================
# Default variables

variable "mfa_age" {
  description = "Max age of valid MFA (in seconds) for roles which require MFA"
  default     = 28800
}
variable "max_session_duration" {
  description = "Maximum CLI/API session duration in seconds between 3600 and 43200"
  default     = 28800
}
variable "admin_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamAdminRole IAM role"
  default     = ["arn:aws:iam::aws:policy/AdministratorAccess"]
}
variable "developer_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamDeveloperRole IAM role"
  default     = ["arn:aws:iam::aws:policy/PowerUserAccess"]
}
variable "readonly_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamReadOnlyRole IAM role"
  default     = ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
}
variable "deployment_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamDeploymentRole IAM role"
  default     = []
}
variable "support_role_policy_arns" {
  description = "List of ARNs of IAM policies to attach to the NHSDServiceTeamSupportRole IAM role"
  default     = []
}

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
