resource "aws_codebuild_project" "di_unit_tests" {
  name           = "${var.project_id}-${var.environment}-unit-test-stage"
  description    = "Runs the unit tests for the DI Project"
  build_timeout  = "5"
  queued_timeout = "5"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE"]
  }


  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "${var.aws_account_id_mgmt}.dkr.ecr.eu-west-2.amazonaws.com/uec-dos/int/tester:latest"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = "local"
    }
    environment_variable {
      name  = "ENVIRONMENT"
      value = var.environment
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
    environment_variable {
      name  = "TESTER_BUILD_PROJECT_NAME"
      value = "${var.project_id}-${var.environment}-build-tester-stage"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-unit-test-stage"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.unit_tests_buildspec.rendered
  }
}

resource "aws_codebuild_project" "di_build" {

  for_each       = local.to_build
  name           = "${var.project_id}-${var.environment}-build-${each.key}-stage"
  description    = "Builds ${each.key} docker container image"
  build_timeout  = "5"
  queued_timeout = "5"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE"]
  }


  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = "local"
    }
    environment_variable {
      name  = "BUILD_TARGET"
      value = "${each.key}-build"
    }
    environment_variable {
      name  = "BUILD_ITEM_NAME"
      value = each.key
    }
    environment_variable {
      name  = "ENVIRONMENT"
      value = var.environment
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
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-build-stage"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.build_buildspec.rendered
  }
}

resource "aws_codebuild_project" "di_deploy_dev" {
  for_each       = local.deploy_envs
  name           = "${var.project_id}-${var.environment}-deploy-${each.key}-stage"
  description    = "Deploy to the ${each.key} environment"
  build_timeout  = "10"
  queued_timeout = "30"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE"]
  }


  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = each.key
    }
    environment_variable {
      name  = "ENVIRONMENT"
      value = each.key
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
    environment_variable {
      name  = "SERVERLESS_BUILD_PROJECT_NAME"
      value = "${var.project_id}-${var.environment}-build-serverless-stage"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-deploy-${each.key}-stage"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.deploy_buildspec.rendered
  }
}

resource "aws_codebuild_project" "di_integration_tests" {
  name           = "${var.project_id}-${var.environment}-integration-test-stage"
  description    = "Runs the integration tests for the DI Project"
  build_timeout  = "60"
  queued_timeout = "30"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE"]
  }


  environment {
    compute_type                = "BUILD_GENERAL1_LARGE"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
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
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-integration-test-stage"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.integration_tests_buildspec.rendered
  }
}


resource "aws_codebuild_project" "di_deploy_fresh" {
  name           = "${var.project_id}-${var.environment}-deploy-fresh-stage"
  description    = "Deploy to the fresh environment"
  build_timeout  = "50"
  queued_timeout = "30"
  service_role   = data.aws_iam_role.pipeline_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type  = "LOCAL"
    modes = ["LOCAL_DOCKER_LAYER_CACHE"]
  }


  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PROFILE"
      value = "dev"
    }
    environment_variable {
      name  = "ENVIRONMENT"
      value = "fresh"
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
      group_name  = "/aws/codebuild/${var.project_id}-${var.environment}-deploy-fresh-stage"
      stream_name = ""
    }
  }
  source {
    type      = "CODEPIPELINE"
    buildspec = data.template_file.deploy_buildspec.rendered
  }
}
