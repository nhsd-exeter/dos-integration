locals {
  deploy_envs      = toset(["dev", "test", "perf"])
  to_build         = toset(["event-sender", "event-processor", "fifo-dlq-handler", "orchestrator", "cr-fifo-dlq-handler", "test-db-checker-handler", "event-replay", "authoriser", "dos-api-gateway", "slack-messenger"])
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
