resource "aws_codepipeline" "stress_test_codepipeline" {
  name     = "${var.project_id}-${var.environment}-stress-test-codepipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

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
        ConnectionArn    = aws_codestarconnections_connection.github.arn
        FullRepositoryId = "${var.github_owner}/${var.github_repo}"
        BranchName       = var.code_pipeline_branch_name
        DetectChanges    = false
      }
    }
  }

  stage {
    name = "PerformanceTests"
    action {
      name            = "StressTests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-stress-test-stage"
      }
    }
  }
}
