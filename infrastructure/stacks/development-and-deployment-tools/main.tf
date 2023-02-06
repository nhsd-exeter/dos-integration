resource "aws_codestarconnections_connection" "github" {
  name          = "${var.project_id}-${var.environment}"
  provider_type = "GitHub"
}

resource "aws_codebuild_source_credential" "github_authenication" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB"
  token       = var.github_token
}

# #tfsec:ignore:aws-kms-auto-rotate-keys
# resource "aws_kms_key" "development_tools_encryption_key" {
#   description              = "${var.environment} signing key for development tools"
#   key_usage                = "ENCRYPT_DECRYPT"
#   customer_master_key_spec = "SYMMETRIC_DEFAULT"
#   policy                   = data.aws_iam_policy_document.kms_policy.json
#   deletion_window_in_days  = 7
#   is_enabled               = true
#   enable_key_rotation      = false
# }

# resource "aws_kms_alias" "development_tools_encryption_key_alias" {
#   name          = "alias/${var.development_tools_encryption_key_alias}"
#   target_key_id = aws_kms_key.development_tools_encryption_key.key_id
# }
