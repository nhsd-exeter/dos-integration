resource "aws_iam_role" "codebuild_role" {
  name = var.codebuild_role

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_codebuild_project" "di_unit_tests" {
  name           = var.unit_test_codebuild_project_name
  description    = "Runs the unit tests for the DI Project"
  build_timeout  = "5"
  queued_timeout = "5"
  service_role   = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type = "NO_CACHE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = var.di_test_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
    privileged_mode             = false

    environment_variable {
      name  = "PROFILE"
      value = var.profile
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.unit_test_codebuild_project_name}"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.unit_tests_buildspec.rendered
  }

  tags = local.standard_tags
}

resource "aws_codebuild_project" "di_e2e_tests" {
  name           = var.e2e_test_codebuild_project_name
  description    = "Runs the E2E/Integration tests for the DI Project"
  build_timeout  = "15"
  queued_timeout = "5"
  service_role   = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type = "NO_CACHE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = var.di_test_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
    privileged_mode             = false

    environment_variable {
      name  = "PROFILE"
      value = var.profile
    }

    environment_variable {
      name  = "BUCKET_NAME"
      value = "uec-pu-di-dev-nhs-uk-importer-s3-bucket"
    }

    environment_variable {
      name  = "GET_DATA_FUNCTION"
      value = "uec-pu-di-dev-get-data"
    }

    environment_variable {
      name  = "PROCESS_CSV_FUNCTION"
      value = "uec-pu-di-dev-process-csv"
    }
    environment_variable {
      name  = "LOG_GROUP_NAME_GET"
      value = "/aws/lambda/uec-pu-di-dev-get-data"
    }
    environment_variable {
      name  = "LOG_GROUP_NAME_PROCESS"
      value = "/aws/lambda/uec-pu-di-dev-process-csv"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.e2e_test_codebuild_project_name}"
      stream_name = ""
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.e2e_test_buildspec.rendered
  }

  tags = local.standard_tags
}

resource "aws_codebuild_project" "di_build_and_deploy" {
  name           = var.build_and_deploy_codebuild_project_name
  description    = "Builds the DI Project and Deploys it"
  build_timeout  = "30"
  queued_timeout = "5"
  service_role   = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type = "NO_CACHE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = var.build_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = var.profile
    }
    environment_variable {
      name  = "ENVIRONMENT"
      value = var.profile
    }
    environment_variable {
      name  = "AWS_ACCOUNT_ID_LIVE_PARENT"
      value = var.aws_account_id_live_parent
    }
    environment_variable {
      name  = "AWS_ACCOUNT_ID_MGMT"
      value = var.aws_account_id_mgmt
    }
    environment_variable {
      name  = "AWS_ACCOUNT_ID_TOOLS"
      value = var.aws_account_id_tools
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
      group_name  = "/aws/codebuild/${var.build_and_deploy_codebuild_project_name}"
      stream_name = ""
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.build_and_deploy_buildspec.rendered
  }

  tags = local.standard_tags
}
