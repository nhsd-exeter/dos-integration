locals {
  integration_make_targets = toset(["integration-test-autoflags-cloudwatch-logs", "integration-test-autoflags-no-logs"])
  deploy_envs              = toset(["test"])
  to_build                 = toset(["service-sync", "service-matcher", "change-event-dlq-handler", "orchestrator", "dos-db-update-dlq-handler", "dos-db-handler", "event-replay", "slack-messenger", "send-email", "ingest-change-event"])
}
