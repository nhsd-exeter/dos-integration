resource "aws_codepipeline" "codepipeline" {
  name     = "${var.project_id}-${var.environment}-codepipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket"
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
    action {
      name            = "Build"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-build-stage"
      }
    }
  }

  stage {
    name = "Deploy"
    action {
      name            = "Deploy_Dev"
      category        = "Build"
      owner           = "AWS"
      run_order       = 1
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-deploy-dev-stage"
      }
    }
    action {
      name            = "Deploy_Test"
      category        = "Build"
      run_order       = 1
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-deploy-test-stage"
      }
    }
    action {
      name            = "Deploy_Performance"
      category        = "Build"
      run_order       = 1
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = "${var.project_id}-${var.environment}-deploy-performance-stage"
      }
    }
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
  source               = "../../modules/s3"
  name                 = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket"
  project_id           = var.project_id
  acl                  = "private"
  profile              = var.profile
  bucket_iam_role      = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket-role"
  iam_role_policy_name = "${var.project_id}-${var.environment}-codepipeline-artefact-bucket-policy"
  log_bucket           = var.texas_s3_logs_bucket
  versioning_enabled   = "true"
  force_destroy        = "true"
}


resource "aws_iam_role" "codepipeline_role" {
  name = "${var.project_id}-${var.environment}-codepipeline-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}
