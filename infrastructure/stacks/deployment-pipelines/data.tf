data "template_file" "deploy_buildspec" {
  template = file("deploy-buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}
