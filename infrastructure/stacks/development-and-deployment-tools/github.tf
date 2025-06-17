resource "aws_codestarconnections_connection" "github" {
  name          = "${var.project_id}-${var.environment}"
  provider_type = "GitHub"
}

resource "aws_codebuild_source_credential" "github_authenication" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB"
  token       = var.github_token
}
