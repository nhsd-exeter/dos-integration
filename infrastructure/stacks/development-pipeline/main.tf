resource "aws_codestarconnections_connection" "github" {
  name          = "${var.project_id}-codestarconnection"
  provider_type = "GitHub"
}
