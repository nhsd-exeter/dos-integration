resource "aws_codepipeline" "release_codepipeline" {
  name     = "${var.project_id}-release-${var.environment}-codepipeline"
  role_arn = data.aws_iam_role.pipeline_role.arn

  artifact_store {
    location = "${var.project_id}-release-${var.environment}-codepipeline-artefact-bucket-mgmt"
    type     = "S3"
  }

  stage {
    name = "Source"
    action {
      category         = "Source"
      name             = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        ConnectionArn    = data.aws_codestarconnections_connection.github.arn
        FullRepositoryId = "${var.github_owner}/${var.github_repo}"
        BranchName       = var.release_pipeline_branch
        DetectChanges    = true
      }
    }
  }

  stage {
    name = "UnitTests"
    action {
      name            = "UnitTests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-dev-unit-test-stage"
      }
    }
  }
  stage {
    name = "Build"
    dynamic "action" {
      for_each = local.to_build
      content {
        name            = "Build_${action.key}"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source_output"]
        version         = "1"
        configuration = {
          ProjectName = "${var.project_id}-dev-build-${action.key}-stage"
        }
      }
    }
  }
  stage {
    name = "Deploy_Non_Prod_Environments"
    dynamic "action" {
      for_each = local.deploy_envs
      content {
        name            = "Deploy_${action.key}"
        category        = "Build"
        owner           = "AWS"
        run_order       = 1
        provider        = "CodeBuild"
        input_artifacts = ["source_output"]
        version         = "1"
        configuration = {
          ProjectName = "${var.project_id}-dev-deploy-stage"
          EnvironmentVariables = jsonencode([
            {
              name  = "PROFILE"
              value = "${action.key}"
              type  = "PLAINTEXT"
            },
            {
              name  = "ENVIRONMENT"
              value = "${var.environment}-${action.key}"
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }
  stage {
    name = "Integration_Test"
    dynamic "action" {
      for_each = local.integration_make_targets
      content {
        name            = "Integration_Test_${action.key}"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source_output"]
        version         = "1"
        configuration = {
          ProjectName = "${var.project_id}-dev-${action.key}"
          EnvironmentVariables = jsonencode([
            {
              name  = "ENVIRONMENT"
              value = "${var.environment}-test"
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }
  stage {
    name = "Deploy_Prod_Environments"
    action {
      name            = "Deploy_Demo"
      category        = "Build"
      owner           = "AWS"
      run_order       = 1
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-dev-deploy-demo-stage"
        EnvironmentVariables = jsonencode([
          {
            name  = "ENVIRONMENT"
            value = "${var.environment}-demo"
            type  = "PLAINTEXT"
          }
        ])
      }
    }
  }
  depends_on = [module.codepipeline_artefact_bucket]
}

module "codepipeline_artefact_bucket" {
  source             = "../../modules/s3"
  name               = "${var.project_id}-release-${var.environment}-codepipeline-artefact-bucket-mgmt"
  project_id         = var.project_id
  acl                = "private"
  versioning_enabled = "true"
  force_destroy      = "true"
}
