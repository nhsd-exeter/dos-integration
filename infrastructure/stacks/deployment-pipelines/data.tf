data "template_file" "deploy_buildspec" {
  template = file("deploy-buildspec.yml")
}

data "template_file" "deploy_configuration_buildspec" {
  template = file("deploy-configuration-buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}
