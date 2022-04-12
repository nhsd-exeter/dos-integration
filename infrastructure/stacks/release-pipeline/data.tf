data "aws_codestarconnections_connection" "development_pipeline_connection" {
  arn = aws_codestarconnections_connection.example.arn
}
data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}
