resource "aws_codebuild_webhook" "tag_release_images_on_branch_delete_webhook" {
  count        = var.environment == "dev" ? 1 : 0
  project_name = aws_codebuild_project.di_tag_release_images_on_branch_delete[0].name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PULL_REQUEST_MERGED"
    }
    filter {
      type    = "HEAD_REF"
      pattern = "refs/heads/release"
    }
  }
  depends_on = [aws_codebuild_project.di_tag_release_images_on_branch_delete]
}

resource "aws_codebuild_project" "di_tag_release_images_on_branch_delete" {
  count          = var.environment == "dev" ? 1 : 0
  name           = "${var.project_id}-${var.environment}-tag-release-images-on-branch-delete-stage"
  description    = "Destroys release environments and release pipelines based on pr merged"
  build_timeout  = "480"
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
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-tag-release-images-on-branch-delete-stage"
      stream_name = ""
    }
  }
  source {
    type            = "GITHUB"
    git_clone_depth = 0 # Full Git Clone
    location        = "https://github.com/nhsd-exeter/dos-integration.git"
    buildspec       = data.template_file.tag_release_images_on_branch_delete_buildspec.rendered
  }

}
