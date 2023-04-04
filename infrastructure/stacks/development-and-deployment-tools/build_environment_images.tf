resource "aws_codebuild_webhook" "build_environment_image_webhook" {
  count        = var.environment == "dev" ? 1 : 0
  project_name = aws_codebuild_project.di_build_environment_image[0].name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }
    filter {
      type    = "HEAD_REF"
      pattern = "refs/heads/task/DSUEC-[0-9]*"
    }
  }
  depends_on = [aws_codebuild_project.di_build_environment_image]
}

resource "aws_codebuild_project" "di_build_environment_image" {
  count          = var.environment == "dev" ? 1 : 0
  name           = "${var.project_id}-${var.environment}-build-environment-image-stage"
  description    = "Builds environment images based on push to task branches"
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
    compute_type                = "BUILD_GENERAL1_LARGE"
    image                       = "aws/codebuild/amazonlinux2-aarch64-standard:2.0"
    type                        = "ARM_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = "dev"
    }
    environment_variable {
      name  = "CB_PROJECT_NAME"
      value = "${var.project_id}-${var.environment}-build-environment-image-stage"
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID_LIVE_PARENT"
      value = var.aws_account_id_live_parent
    }
    environment_variable {
      name  = "AWS_ACCOUNT_ID_MGMT"
      value = var.aws_account_id_mgmt
    }
    environment_variable {
      name  = "AWS_ACCOUNT_ID_NONPROD"
      value = var.aws_account_id_nonprod
    }
    environment_variable {
      name  = "AWS_ACCOUNT_ID_PROD"
      value = var.aws_account_id_prod
    }
    environment_variable {
      name  = "AWS_ACCOUNT_ID_IDENTITIES"
      value = var.aws_account_id_identities
    }
  }
  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-build-environment-image-stage"
      stream_name = ""
    }
  }
  source {
    type            = "GITHUB"
    git_clone_depth = 0
    location        = var.github_url
    buildspec       = data.template_file.build_arm_buildspec.rendered
  }

}
