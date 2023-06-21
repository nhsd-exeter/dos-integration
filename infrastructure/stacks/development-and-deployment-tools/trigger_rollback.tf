resource "aws_codebuild_project" "trigger_rollback" {
  name           = "${var.project_id}-${var.environment}-trigger-rollback"
  description    = "Trigger rollback"
  build_timeout  = "30"
  queued_timeout = "5"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

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
    environment_variable {
      name  = "GIT_REPO_URL"
      value = var.github_url
    }
    environment_variable {
      name  = "PROJECT_REPO"
      value = "${var.github_owner}/${var.github_repo}"
    }
    environment_variable {
      name  = "ROLLBACK_PROJECT_NAME"
      value = aws_codebuild_project.blue_green_rollback_stage.name
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-trigger-rollback"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = file("buildspecs/trigger-rollback-buildspec.yml")
  }
}
