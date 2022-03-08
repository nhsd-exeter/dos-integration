resource "aws_codebuild_source_credential" "github_authenication" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB"
  token       = var.github_token
}
