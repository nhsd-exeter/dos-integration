resource "aws_codebuild_source_credential" "github_authenication" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB"
  token       = var.github_token
}

resource "aws_sns_topic" "live_pipeline_notification_topic" {
  name = "${var.project_id}-live-deploy-stage-notifications"
}

resource "aws_sns_topic" "demo_pipeline_notification_topic" {
  name = "${var.project_id}-demo-deploy-stage-notifications"
}
