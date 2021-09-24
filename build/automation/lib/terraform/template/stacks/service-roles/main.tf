module "NAME_TEMPLATE_TO_REPLACE-iam-roles" {
  source  = "../../modules/iam-roles"
  context = local.context

  nhsd_identities_account_id = var.terraform_nhsd_identities_account_id

  admin_role_policy_arns      = var.terraform_admin_role_policy_arns
  developer_role_policy_arns  = var.terraform_developer_role_policy_arns
  readonly_role_policy_arns   = var.terraform_readonly_role_policy_arns
  deployment_role_policy_arns = var.terraform_deployment_role_policy_arns
  support_role_policy_arns    = var.terraform_support_role_policy_arns
}
