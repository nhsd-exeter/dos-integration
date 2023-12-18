resource "aws_codepipeline" "development_pipeline" {
  name     = "${var.project_id}-${var.environment}-development-pipeline"
  role_arn = data.aws_iam_role.pipeline_role.arn

  artifact_store {
    location = "${var.project_id}-${var.environment}-development-pipeline-artefact-bucket"
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
        ConnectionArn    = aws_codestarconnections_connection.github.arn
        FullRepositoryId = "${var.github_owner}/${var.github_repo}"
        BranchName       = var.development_pipeline_branch_name
        DetectChanges    = true
      }
    }
  }

  stage {
    name = "Unit_Tests"
    action {
      name            = "UnitTests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.di_unit_tests_stage.name
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
          ProjectName = aws_codebuild_project.di_build_image_stage.name
          EnvironmentVariables = jsonencode([
            {
              name  = "BUILD_ITEM_NAME"
              value = "${action.key}"
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
  }
  stage {
    name = "Deploy_Test_Environments"
    dynamic "action" {
      for_each = local.development_nonprod_environments
      content {
        name            = "Deploy_${action.value["ENVIRONMENT"]}"
        category        = "Build"
        owner           = "AWS"
        run_order       = 1
        provider        = "CodeBuild"
        input_artifacts = ["source_output"]
        version         = "1"
        configuration = {
          ProjectName = aws_codebuild_project.di_full_deploy_stage.name
          EnvironmentVariables = jsonencode([
            {
              name  = "AWS_ACCOUNT"
              value = "${action.value["AWS_ACCOUNT"]}"
              type  = "PLAINTEXT"
            },
            {
              name  = "PROFILE"
              value = "${action.value["PROFILE"]}"
              type  = "PLAINTEXT"
            },
            {
              name  = "ENVIRONMENT"
              value = "${action.value["ENVIRONMENT"]}"
              type  = "PLAINTEXT"
            }
          ])
        }
      }
    }
    dynamic "action" {
      for_each = local.integration_test_tags
      content {
        name            = "Integration_Test_${action.key}"
        category        = "Build"
        owner           = "AWS"
        provider        = "CodeBuild"
        input_artifacts = ["source_output"]
        version         = "1"
        run_order       = 2
        configuration = {
          ProjectName = aws_codebuild_project.di_integration_tests[action.key].name
          EnvironmentVariables = jsonencode([
            {
              name  = "PROFILE"
              value = "dev"
              type  = "PLAINTEXT"
            },
            {
              name  = "SHARED_ENVIRONMENT"
              value = "test"
              type  = "PLAINTEXT"
            },
            {
              name  = "BLUE_GREEN_ENVIRONMENT"
              value = "test"
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
        ProjectName = aws_codebuild_project.di_full_deploy_stage.name
        EnvironmentVariables = jsonencode([
          {
            name  = "PROFILE"
            value = "demo"
            type  = "PLAINTEXT"
          },
          {
            name  = "ENVIRONMENT"
            value = "demo"
            type  = "PLAINTEXT"
          },
          {
            name  = "AWS_ACCOUNT"
            value = "PROD"
            type  = "PLAINTEXT"
          }
        ])
      }
    }

    action {
      name            = "Smoke_Test_Demo"
      category        = "Build"
      owner           = "AWS"
      run_order       = 2
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = aws_codebuild_project.production_smoke_test.name
        EnvironmentVariables = jsonencode([
          {
            name  = "PROFILE"
            value = "demo"
            type  = "PLAINTEXT"
          },
          {
            name  = "ENVIRONMENT"
            value = "demo"
            type  = "PLAINTEXT"
          },
          {
            name  = "AWS_ACCOUNT"
            value = "PROD"
            type  = "PLAINTEXT"
          }
        ])
      }
    }
  }

  depends_on = [
    module.development_pipeline_artefact_bucket,
    aws_codebuild_project.di_unit_tests_stage,
    aws_codebuild_project.di_build_image_stage,
    aws_codebuild_project.di_full_deploy_stage,
    aws_codebuild_project.di_integration_tests,
    aws_codebuild_project.production_smoke_test,
  ]
}


module "development_pipeline_artefact_bucket" {
  source             = "../../modules/s3"
  name               = "${var.project_id}-${var.environment}-development-pipeline-artefact-bucket"
  project_id         = var.project_id
  acl                = "private"
  versioning_enabled = "true"
  force_destroy      = "true"
}
