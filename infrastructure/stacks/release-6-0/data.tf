data "template_file" "release_6_0_buildspec" {
  template = file("release_6_0_buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}
