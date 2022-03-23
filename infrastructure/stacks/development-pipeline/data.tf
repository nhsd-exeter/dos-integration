data "template_file" "unit_tests_buildspec" {
  template = file("unit-tests-buildspec.yml")
}

data "template_file" "build_buildspec" {
  template = file("build-buildspec.yml")
}

data "template_file" "build_image_buildspec" {
  template = file("build-image-buildspec.yml")
}

data "template_file" "deploy_buildspec" {
  template = file("deploy-buildspec.yml")
}

data "template_file" "integration_tests_buildspec" {
  template = file("integration-tests-buildspec.yml")
}

data "template_file" "delete_task_environment_from_tag_buildspec" {
  template = file("delete-task-environment-from-tag-buildspec.yml")
}

data "aws_iam_role" "pipeline_role" {
  name = "UECPUPipelineRole"
}

locals {
  deploy_envs = toset(["dev", "test", "perf"])
  to_build    = toset(["event-sender", "event-processor", "fifo-dlq-handler", "orchestrator", "cr-fifo-dlq-handler", "test-db-checker-handler", "event-replay", "authoriser", "dos-api-gateway", "slack_messenger"])
  independent_build_images = {
    tester = {
      "filematch" = "requirement"
    }
    serverless = {
      "filematch" = "serverless.yml"
    }
  }
}
