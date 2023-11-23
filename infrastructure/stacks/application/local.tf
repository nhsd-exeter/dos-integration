locals {
  deployment_secrets              = jsondecode(data.aws_secretsmanager_secret_version.deployment_secrets.secret_string)
  slack_webhook_url               = local.deployment_secrets["SLACK_WEBHOOK"]
  project_system_email_address    = local.deployment_secrets["DI_SYSTEM_MAILBOX_ADDRESS"]
  project_team_email_address      = local.deployment_secrets["DI_TEAM_MAILBOX_ADDRESS"]
  dos_db_read_and_write_user_name = local.deployment_secrets["DOS_DB_DI_USERNAME"]
  dos_db_read_only_user_name      = local.deployment_secrets[var.dos_db_read_only_user_name_secret_key]
}
