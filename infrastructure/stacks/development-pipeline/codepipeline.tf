resource "aws_codepipeline" "codepipeline" {
  name     = "${var.project_id}-${var.environment}-codepipeline"
  role_arn = data.aws_iam_role.pipeline_role.arn

  artifact_store {
    location = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket-mgmt"
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
        BranchName       = var.code_pipeline_branch_name
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
        ProjectName = "${var.project_id}-${var.environment}-unit-test-stage"
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
          ProjectName = "${var.project_id}-${var.environment}-build-${action.key}-stage"
        }
      }
    }
  }
  stage {
    name = "Deploy"
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
          ProjectName = "${var.project_id}-${var.environment}-deploy-${action.key}-stage"
        }
      }
    }
    # action {
    #   name            = "Deploy_fresh"
    #   category        = "Build"
    #   owner           = "AWS"
    #   run_order       = 1
    #   provider        = "CodeBuild"
    #   input_artifacts = ["source_output"]
    #   version         = "1"
    #   configuration = {
    #     ProjectName = "${var.project_id}-${var.environment}-deploy-fresh-stage"
    #   }
    # }
  }

  stage {
    name = "Integration_Test"
    action {
      name            = "Integration_Test"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-integration-test-stage"
      }
    }
  }

}
resource "aws_codestarconnections_connection" "github" {
  name          = "${var.project_id}-codestarconnection"
  provider_type = "GitHub"
}
module "codepipeline_artefact_bucket" {
  source     = "../../modules/s3"
  name       = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket-mgmt"
  project_id = var.project_id
  acl        = "private"
  profile    = var.profile
  # bucket_iam_role      = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket-role"
  # iam_role_policy_name = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket-policy"
  versioning_enabled = "true"
  force_destroy      = "true"
}
