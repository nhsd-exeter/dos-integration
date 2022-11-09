resource "aws_codebuild_webhook" "build_cicd_shared_resources_artefact_webhook" {
  count        = var.environment == "dev" ? 1 : 0
  project_name = aws_codebuild_project.di_build_cicd_shared_resources_artefact[0].name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }

    filter {
      type    = "HEAD_REF"
      pattern = "^refs/tags/.*-shared-resources"
    }
  }
  depends_on = [aws_codebuild_project.di_build_cicd_shared_resources_artefact]
}

resource "aws_codebuild_project" "di_build_cicd_shared_resources_artefact" {
  count          = var.environment == "dev" ? 1 : 0
  name           = "${var.project_id}-${var.environment}-build-cicd-shared-resources-artefact"
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
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "CB_PROJECT_NAME"
      value = "${var.project_id}-${var.environment}-build-cicd-shared-resources-artefact"
    }
    environment_variable {
      name  = "CICD_ARTIFACT_BUCKET"
      value = "${var.project_id}-${var.environment}-cicd-shared-resources-pipeline-artefact"
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
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-build-cicd-shared-resources-artefact-stage"
      stream_name = ""
    }
  }
  source {
    type            = "GITHUB"
    git_clone_depth = 0
    location        = "https://github.com/nhsd-exeter/dos-integration.git"
    buildspec       = data.template_file.build_cicd_shared_resources_artefact_buildspec.rendered
  }
  depends_on = [
    module.cicd_pipeline_artefact_bucket
  ]
}
