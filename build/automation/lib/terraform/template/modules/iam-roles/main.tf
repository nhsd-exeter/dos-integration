module "iam-roles-default" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-roles"
  version = "3.6.0"

  max_session_duration = var.max_session_duration
  mfa_age              = var.mfa_age

  trusted_role_arns = ["arn:aws:iam::${var.nhsd_identities_account_id}:root"]

  create_admin_role       = true
  admin_role_name         = "NHSDServiceTeamAdminRole"
  admin_role_policy_arns  = var.admin_role_policy_arns
  admin_role_requires_mfa = true
  admin_role_tags         = var.context.tags

  create_poweruser_role       = true
  poweruser_role_name         = "NHSDServiceTeamDeveloperRole"
  poweruser_role_policy_arns  = var.developer_role_policy_arns
  poweruser_role_requires_mfa = true
  poweruser_role_tags         = var.context.tags

  create_readonly_role       = true
  readonly_role_name         = "NHSDServiceTeamReadOnlyRole"
  readonly_role_policy_arns  = var.readonly_role_policy_arns
  readonly_role_requires_mfa = true
  readonly_role_tags         = var.context.tags
}

module "iam-role-deployment" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "3.6.0"
  tags    = var.context.tags

  max_session_duration = var.max_session_duration
  mfa_age              = var.mfa_age

  trusted_role_arns = ["arn:aws:iam::${var.nhsd_identities_account_id}:root"]

  create_role             = true
  role_name               = "NHSDServiceTeamDeploymentRole"
  custom_role_policy_arns = var.deployment_role_policy_arns
  role_requires_mfa       = true
}

module "iam-role-support" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "3.6.0"
  tags    = var.context.tags

  max_session_duration = var.max_session_duration
  mfa_age              = var.mfa_age

  trusted_role_arns = ["arn:aws:iam::${var.nhsd_identities_account_id}:root"]

  create_role             = true
  role_name               = "NHSDServiceTeamSupportRole"
  custom_role_policy_arns = var.support_role_policy_arns
  role_requires_mfa       = true
}
