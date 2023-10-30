locals {
  ip_address_secret       = jsondecode(data.aws_secretsmanager_secret_version.ip_address_secret.secret_string)
  ip_addresses            = values(local.ip_address_secret)
  allowlist_ips_hash      = md5(join(",", local.ip_addresses))
  deployment_secrets      = jsondecode(data.aws_secretsmanager_secret_version.deployment_secrets.secret_string)
  aws_sso_role            = local.deployment_secrets["AWS_SSO_ROLE"]
  aws_sso_read_write_role = var.aws_account_name != "prod" ? local.deployment_secrets["AWS_SSO_READ_WRITE_ROLE"] : ""
}
