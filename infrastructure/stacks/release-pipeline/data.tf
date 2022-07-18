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
  to_build    = toset(["event-sender", "event-processor", "fifo-dlq-handler", "orchestrator", "cr-fifo-dlq-handler", "test-db-checker-handler", "event-replay", "slack-messenger", "authoriser", "dos-api-gateway"])
}
