resource "aws_codepipeline" "codepipeline" {
  name     = "${var.prefix}-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.artifacts.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = var.codestar_connection_arn
        FullRepositoryId = var.repository_id
        BranchName       = var.branch_name
        OutputArtifactFormat : "CODE_ZIP"
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.example.name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name            = "CreateChangeSet"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "CloudFormation"
      input_artifacts = ["build_output"]
      version         = "1"
      run_order       = 1

      configuration = {
        ActionMode         = "CHANGE_SET_REPLACE"
        Capabilities       = "CAPABILITY_IAM,CAPABILITY_AUTO_EXPAND"
        RoleArn            = aws_iam_role.deployment_role.arn
        StackName          = var.cloudformation_stack_name
        TemplatePath       = "build_output::packaged.yaml"
        ChangeSetName      = "change-set-execute"
      }
    }

    action {
      name      = "ExecuteChangeSet"
      category  = "Deploy"
      owner     = "AWS"
      provider  = "CloudFormation"
      version   = "1"
      run_order = 2

      configuration = {
        ActionMode    = "CHANGE_SET_EXECUTE"
        StackName     = var.cloudformation_stack_name
        ChangeSetName = "change-set-execute"
      }
    }
  }

  tags = {
    provisioned_by = "terraform"
  }
}


resource "aws_iam_role" "codepipeline_role" {
  name     = "${var.prefix}-pipeline-role"
  tags = {
    provisioned_by = "terraform"
  }

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

resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "${var.prefix}-pipeline-policy"
  role = aws_iam_role.codepipeline_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": [
        "${aws_s3_bucket.artifacts.arn}",
        "${aws_s3_bucket.artifacts.arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:DescribeStacks",
        "cloudformation:CreateChangeSet",
        "cloudformation:ExecuteChangeSet",
        "cloudformation:DescribeChangeSet",
        "cloudformation:DeleteChangeSet"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": "*"
    },
    {
        "Effect": "Allow",
        "Action": [
            "codestar-connections:UseConnection"
        ],
        "Resource": "*"
    },
    {
        "Action": [
            "appconfig:StartDeployment",
            "appconfig:GetDeployment",
            "appconfig:StopDeployment"
        ],
        "Resource": "*",
        "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role" "deployment_role" {
  name = "${var.prefix}-deployment-role"
  tags = {
    provisioned_by = "terraform"
  }

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudformation.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "admin_access_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  role       = aws_iam_role.deployment_role.name
}
