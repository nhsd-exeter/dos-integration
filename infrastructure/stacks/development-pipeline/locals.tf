locals {
  deploy_envs              = toset(["test", "perf"])
  to_build                 = toset(["service-sync", "service-matcher", "change-event-dlq-handler", "orchestrator", "dos-db-update-dlq-handler", "dos-db-handler", "event-replay", "slack-messenger", "send-email"])
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
