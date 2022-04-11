resource "aws_codebuild_webhook" "live_deployment_webhook" {
  project_name = aws_codebuild_project.di_deploy_live.name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }

    filter {
      type    = "HEAD_REF"
      pattern = "^refs/tags/.*-live-deploy"
    }
  }
}
resource "aws_codebuild_project" "di_deploy_live" {
  name           = "${var.project_id}-live-deploy-stage"
  description    = "Deploy to the live environment"
  build_timeout  = "30"
  queued_timeout = "30"
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
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = "live"
    }

    environment_variable {
      name  = "ENVIRONMENT"
      value = "live"
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
      group_name  = "/aws/codebuild/${var.project_id}-live-deploy-stage"
      stream_name = ""
    }
  }
  source_version = "master"
  source {
    type            = "GITHUB"
    git_clone_depth = 0
    location        = "https://github.com/nhsd-exeter/dos-integration.git"
    buildspec       = data.template_file.deploy_buildspec.rendered
  }
  depends_on = [aws_codebuild_source_credential.github_authenication]
}

resource "aws_codestarnotifications_notification_rule" "live_notification_rule" {
  detail_type    = "BASIC"
  event_type_ids = ["codebuild-project-build-state-failed", "codebuild-project-build-state-succeeded", "codebuild-project-build-state-in-progress", "codebuild-project-build-state-stopped", "codebuild-project-build-phase-failure", "codebuild-project-build-phase-success"]

  name     = "${var.project_id}-live-notification-rule"
  resource = aws_codebuild_project.di_deploy_live.arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}
