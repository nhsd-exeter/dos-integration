data "template_file" "unit_tests_buildspec" {
  template = file("unit-tests-buildspec.yml")
}

data "template_file" "build_buildspec" {
  template = file("build-buildspec.yml")
}

data "template_file" "deploy_buildspec" {
  template = file("deploy-buildspec.yml")
}


data "template_file" "integration_tests_buildspec" {
  template = file("integration-tests-buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}

locals {
  deploy_envs = toset(["dev", "test", "perf"])
  to_build    = toset(["event-sender", "event-processor", "fifo-dlq-handler", "eventbridge-dlq-handler", "test-db-checker-handler", "event-replay"])
}
