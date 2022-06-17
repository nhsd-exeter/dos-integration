data "template_file" "perf_buildspec" {
  template = file("perf-buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}

locals {
  performance_tests = toset(["stress", "load"])
}
