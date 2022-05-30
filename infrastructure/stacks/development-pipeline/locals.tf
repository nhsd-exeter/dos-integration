locals {
  deploy_envs      = toset(["dev", "test", "perf"])
  to_build         = toset(["event-sender", "event-processor", "fifo-dlq-handler", "orchestrator", "cr-fifo-dlq-handler", "test-db-checker-handler", "event-replay", "authoriser", "dos-api-gateway", "slack-messenger"])
  integration_tags = toset(["pharmacy_cloudwatch_queries", "pharmacy_no_log_searches"])
  independent_build_images = {
    tester = {
      "filematch" = "requirement"
    }
    serverless = {
      "filematch" = "serverless.yml"
    }
  }

}
