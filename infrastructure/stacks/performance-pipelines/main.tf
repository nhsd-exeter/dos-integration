module "codepipeline_artefact_bucket" {
  source             = "../../modules/s3"
  name               = "${var.project_id}-${var.environment}-performance-codepipeline-artefact-bucket"
  project_id         = var.project_id
  acl                = "private"
  profile            = var.profile
  versioning_enabled = "true"
  force_destroy      = "true"
}
