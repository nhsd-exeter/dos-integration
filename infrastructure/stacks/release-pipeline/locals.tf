locals {
  deploy_envs = toset(["test"])
  to_build    = toset(["service-sync", "service-matcher", "change-event-dlq-handler", "orchestrator", "dos-db-update-dlq-handler", "dos-db-handler", "event-replay", "slack-messenger", "send-email", "ingest-change-event"])
}
