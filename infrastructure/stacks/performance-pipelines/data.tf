data "terraform_remote_state" "development_pipeline" {
  backend = "s3"
  config = {
    bucket = var.service_state_bucket
    key    = var.development_pipeline_state
    region = var.aws_region
  }
}

data "template_file" "stress_tests_buildspec" {
  template = file("stress-test-buildspec.yml")
}

data "template_file" "load_tests_buildspec" {
  template = file("load-test-buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}

locals {
  performance_tests = {
    stress = {
      buildspec = data.template_file.stress_tests_buildspec.rendered
    }
    load = {
      buildspec = data.template_file.load_tests_buildspec.rendered
    }
  }
}
