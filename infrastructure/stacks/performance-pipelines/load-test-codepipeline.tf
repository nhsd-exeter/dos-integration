resource "aws_codepipeline" "load_test_codepipeline" {
  name     = "${var.project_id}-${var.environment}-load-test-codepipeline"
  role_arn = data.aws_iam_role.pipeline_role.arn

  artifact_store {
    location = "${var.project_id}-${var.environment}-performance-codepipeline-artefact-bucket"
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
        ConnectionArn    = data.terraform_remote_state.development_pipeline.outputs.codestarconnection_arn
        FullRepositoryId = "${var.github_owner}/${var.github_repo}"
        BranchName       = var.perf_pipeline_branch_name
        DetectChanges    = false
      }
    }
  }

  stage {
    name = "PerformanceTests"
    action {
      name            = "LoadTests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-load-test-stage"
      }
    }
  }
}
