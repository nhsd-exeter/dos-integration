data "terraform_remote_state" "development_pipeline" {
  backend = "s3"
  config = {
    bucket = var.service_state_bucket
    key    = var.development_pipeline_state
    region = var.aws_region
  }
}

data "template_file" "perf_buildspec" {
  template = file("perf-buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}

locals {
  performance_tests = toset(["stress", "load"])
}
