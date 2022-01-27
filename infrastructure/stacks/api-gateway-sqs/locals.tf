locals {
  ip_address_secret  = jsondecode(data.aws_secretsmanager_secret_version.ip_address_secret.secret_string)[var.ip_address_secret_key]
  ip_addresses       = values(jsondecode(local.ip_address_secret))
  allowlist_ips_hash = md5(join(",", local.ip_addresses))
}
