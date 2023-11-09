locals {
  development_nonprod_environments = {
    # Environments to deploy in the nonprod account from the development pipeline
    "test" = {
      "PROFILE"     = "dev",
      "ENVIRONMENT" = "test",
      "AWS_ACCOUNT" = "NONPROD"
    }
  }
  development_prod_environments = {
    # Environments to deploy in the prod account from the development pipeline
    "test" = {
      "PROFILE"     = "demo",
      "ENVIRONMENT" = "demo",
      "AWS_ACCOUNT" = "PROD"
    }
  }
  cicd_nonprod_environments = {
    # Environments to deploy in the nonprod account from the cicd pipeline
    "cicd" = {
      "PROFILE"            = "dev",
      "SHARED_ENVIRONMENT" = "cicd-test",
      "AWS_ACCOUNT"        = "NONPROD"
    }
  }
  cicd_prod_environments = {
    # Environments to deploy in the prod account from the cicd pipeline
    "cicd" = {
      "PROFILE"            = "demo",
      "SHARED_ENVIRONMENT" = "cicd-release",
      "AWS_ACCOUNT"        = "PROD"
    }
  }
  to_build              = toset(["service-sync", "service-matcher", "change-event-dlq-handler", "dos-db-update-dlq-handler", "dos-db-handler", "event-replay", "slack-messenger", "send-email", "ingest-change-event", "quality-checker"])
  integration_test_tags = toset(["general", "validation", "slack_and_infrastructure", "reporting", "opening_times"])
  independent_build_images = {
    tester = {
      "filematch" = "requirement"
    }
    serverless = {
      "filematch" = "serverless.yml"
    }
  }
  default_environment_variables = {
    "AWS_DEFAULT_REGION"         = var.aws_region
    "AWS_ACCOUNT_ID_LIVE_PARENT" = var.aws_account_id_live_parent
    "AWS_ACCOUNT_ID_MGMT"        = var.aws_account_id_mgmt
    "AWS_ACCOUNT_ID_NONPROD"     = var.aws_account_id_nonprod
    "AWS_ACCOUNT_ID_IDENTITIES"  = var.aws_account_id_identities
    "AWS_ACCOUNT_ID_PROD"        = var.aws_account_id_prod
    "PIPELINE_BUILD_ROLE"        = "UECDoSINTPipelineBuildRole"
  }
}
