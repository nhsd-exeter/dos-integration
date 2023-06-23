resource "aws_codebuild_webhook" "destroy_nonprod_environment_on_pr_merged_deployment_webhook" {
  count        = var.environment == "dev" ? 1 : 0
  project_name = aws_codebuild_project.di_destroy_nonprod_environment_on_pr_merged[0].name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PULL_REQUEST_MERGED"
    }
    filter {
      type    = "HEAD_REF"
      pattern = "refs/heads/task"
    }
  }
}

resource "aws_codebuild_project" "di_destroy_nonprod_environment_on_pr_merged" {
  count          = var.environment == "dev" ? 1 : 0
  name           = "${var.project_id}-${var.environment}-destroy-nonprod-environment-on-pr-merged-stage"
  description    = "Destroys nonprod environment based on pr merged"
  build_timeout  = "30"
  queued_timeout = "5"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE"]
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = "dev"
    }
    environment_variable {
      name  = "CB_PROJECT_NAME"
      value = "${var.project_id}-${var.environment}-destroy-nonprod-environment-on-pr-merged-stage"
    }
    dynamic "environment_variable" {
      for_each = local.default_environment_variables
      content {
        name  = environment_variable.key
        value = environment_variable.value
      }
    }

    environment_variable {
      name  = "SERVERLESS_BUILD_PROJECT_NAME"
      value = "${var.project_id}-${var.environment}-build-serverless-stage"
    }
  }
  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-destroy-nonprod-environment-on-pr-merged-stage"
      stream_name = ""
    }
  }
  source {
    type            = "GITHUB"
    git_clone_depth = 0
    location        = var.github_url
    buildspec       = data.template_file.delete_nonprod_environment_on_pr_merged_buildspec.rendered
  }

}
