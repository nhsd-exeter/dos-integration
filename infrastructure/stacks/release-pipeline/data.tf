data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}

data "aws_sns_topic" "development_pipeline_topic" {
  name = "${var.project_id}-dev-pipeline-topic"
}

data "aws_codestarconnections_connection" "github" {
  name = "uec-dos-int-dev"
}
