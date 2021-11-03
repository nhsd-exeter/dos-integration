resource "aws_codepipeline" "codepipeline" {
  name     = var.development_pipeline_name
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = var.codepipeline_artefact_bucket_name
    type     = "S3"
  }

  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "S3"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        S3Bucket             = "uec-pu-di-dev-nhs-uk-importer-s3-bucket"
        S3ObjectKey          = "profile-updater2.zip"
        PollForSourceChanges = "true"
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
        ProjectName = var.unit_test_codebuild_project_name
      }
    }
  }

  stage {
    name = "BuildAndDeploy"
    action {
      name            = "BuildAndDeploy"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = var.build_and_deploy_codebuild_project_name
      }
    }
  }

  stage {
    name = "Test"
    action {
      name            = "E2ETests"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"
      configuration = {
        ProjectName = var.e2e_test_codebuild_project_name
      }
    }
  }
}

module "codepipeline_artefact_bucket" {
  source               = "../../modules/s3"
  name                 = var.codepipeline_artefact_bucket_name
  service_name         = var.service_name
  acl                  = "private"
  profile              = var.profile
  bucket_iam_role      = "${var.codepipeline_artefact_bucket_name}-role"
  iam_role_policy_name = "${var.codepipeline_artefact_bucket_name}-policy"
  log_bucket           = var.texas_s3_logs_bucket
  versioning_enabled   = "true"
  force_destroy        = "true"
}


resource "aws_iam_role" "codepipeline_role" {
  name = var.codepipeline_role

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
