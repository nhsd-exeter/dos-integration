resource "aws_codebuild_webhook" "build_cicd_blue_green_artefact_webhook" {
  count        = var.environment == "dev" ? 1 : 0
  project_name = aws_codebuild_project.di_build_cicd_blue_green_artefact[0].name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }

    filter {
      type    = "HEAD_REF"
      pattern = "^refs/tags/.*-blue-green-deployment"
    }
  }
  depends_on = [aws_codebuild_project.di_build_cicd_blue_green_artefact]
}

resource "aws_codebuild_project" "di_build_cicd_blue_green_artefact" {
  count          = var.environment == "dev" ? 1 : 0
  name           = "${var.project_id}-${var.environment}-build-cicd-blue-green-artefact"
  description    = "Builds artefacts based on tag for CI/CD Pipeline"
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
      name  = "CB_PROJECT_NAME"
      value = "${var.project_id}-${var.environment}-build-cicd-blue-green-artefact"
    }
    environment_variable {
      name  = "CICD_BLUE_GREEN_DEPLOYMENT_PIPELINE"
      value = var.cicd_blue_green_deployment_pipeline_name
    }
    environment_variable {
      name  = "CICD_ARTIFACT_BUCKET"
      value = var.cicd_blue_green_deployment_pipeline_artefact_bucket
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
    environment_variable {
      name  = "NEW_VERSION_PARAMETER_NAME"
      value = var.blue_green_deployment_new_version_parameter_name
    }

  }
  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-build-cicd-blue-green-artefact-stage"
      stream_name = ""
    }
  }
  source {
    type            = "GITHUB"
    git_clone_depth = 0
    location        = var.github_url
    buildspec       = data.template_file.build_cicd_blue_green_deployment_artefact_buildspec.rendered
  }
  depends_on = [module.cicd_blue_green_deployment_pipeline_artefact_bucket]
}
