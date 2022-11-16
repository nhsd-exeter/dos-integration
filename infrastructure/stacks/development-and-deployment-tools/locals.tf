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
  to_build                 = toset(["service-sync", "service-matcher", "change-event-dlq-handler", "orchestrator", "dos-db-update-dlq-handler", "dos-db-handler", "event-replay", "slack-messenger", "send-email", "ingest-change-event"])
  integration_make_targets = toset(["integration-test-autoflags-cloudwatch-logs", "integration-test-autoflags-no-logs"])
  independent_build_images = {
    tester = {
      "filematch" = "requirement"
    }
    serverless = {
      "filematch" = "serverless.yml"
    }
  }

}
