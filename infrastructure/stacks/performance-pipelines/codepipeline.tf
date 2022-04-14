resource "aws_codepipeline" "performance_test_codepipeline" {
  for_each = local.performance_tests
  name     = "${var.project_id}-${var.environment}-${each.key}-test-codepipeline"
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
      name            = "${title(each.key)}Tests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-${each.key}-test-stage"
      }
    }
  }
}

resource "aws_codestarnotifications_notification_rule" "pipeline_notifications" {
  for_each       = local.performance_tests
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = "${var.project_id}-${var.environment}-stress-test-pipeline-notification"
  resource = aws_codepipeline.performance_test_codepipeline[each.key].arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
  depends_on = [
    aws_codebuild_project.di_performance_tests
  ]
}
