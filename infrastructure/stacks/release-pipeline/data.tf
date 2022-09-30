data "terraform_remote_state" "development_pipeline" {
  backend = "s3"
  config = {
    bucket = var.service_state_bucket
    key    = var.development_pipeline_state
    region = var.aws_region
  }
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}

data "aws_sns_topic" "development_pipeline_topic" {
  name = "${var.project_id}-dev-pipeline-topic"
}

locals {
  deploy_envs = toset(["test", "perf"])
  to_build    = toset(["service-sync", "service-matcher", "change-event-dlq-handler", "orchestrator", "dos-db-update-dlq-handler", "dos-db-handler", "event-replay", "slack-messenger", "send-email"])
}
