resource "aws_cloudwatch_event_rule" "setup_dos_environment_rule" {
  count               = var.environment == "dev" ? 1 : 0
  name                = "${var.project_id}-${var.environment}-setup-dos-environment-rule"
  description         = "Trigger the setup of a DOS environment on a schedule"
  schedule_expression = "cron(0 8 * * ? *)"
}

resource "aws_cloudwatch_event_target" "setup_dos_environment_trigger" {
  count    = var.environment == "dev" ? 1 : 0
  rule     = aws_cloudwatch_event_rule.setup_dos_environment_rule[0].name
  arn      = aws_codebuild_project.setup_dos_environment[0].arn
  role_arn = data.aws_iam_role.pipeline_role.arn
}

resource "aws_codebuild_project" "setup_dos_environment" {
  count          = var.environment == "dev" ? 1 : 0
  name           = "${var.project_id}-${var.environment}-setup-dos-environment-stage"
  description    = "Setup the DoS RegressionDI Environment"
  build_timeout  = "60"
  queued_timeout = "30"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_SOURCE_CACHE", "LOCAL_DOCKER_LAYER_CACHE"]
  }


  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = "test"
    }
    environment_variable {
      name  = "ENVIRONMENT"
      value = "test"
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
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-setup-dos-environment-stage"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.setup_dos_environment_buildspec.rendered
  }
  vpc_config {
    security_group_ids = [
      aws_security_group.uec_dos_int_int_test_sg[0].id,
    ]
    subnets = [
      data.aws_subnet.vpc_subnet_one.id,
      data.aws_subnet.vpc_subnet_two.id,
      data.aws_subnet.vpc_subnet_three.id
    ]
    vpc_id = data.aws_vpc.texas_mgmt_vpc.id
  }
}