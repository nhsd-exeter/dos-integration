resource "aws_codestarconnections_connection" "github" {
  name          = "${var.project_id}-codestarconnection"
  provider_type = "GitHub"

}
module "codepipeline_artefact_bucket" {
  source               = "../../modules/s3"
  name                 = "${var.project_id}-${var.environment}-performance-codepipeline-artefact-bucket"
  project_id           = var.project_id
  acl                  = "private"
  profile              = var.profile
  bucket_iam_role      = "${var.project_id}-${var.environment}-performance-codepipeline-artefact-bucket-role"
  iam_role_policy_name = "${var.project_id}-${var.environment}-performance-codepipeline-artefact-bucket-policy"
  log_bucket           = var.texas_s3_logs_bucket
  versioning_enabled   = "true"
  force_destroy        = "true"
}
