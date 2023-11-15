output "lambda_versions" {
  value = {
    "change_event_dlq_handler"  = var.change_event_dlq_handler_version
    "dos_db_handler"            = var.dos_db_handler_version
    "dos_db_update_dlq_handler" = var.dos_db_update_dlq_handler_version
    "event_replay"              = var.event_replay_version
    "ingest_change_event"       = var.ingest_change_event_version
    "send_email"                = var.send_email_version
    "service_matcher"           = var.service_matcher_version
    "service_sync"              = var.service_sync_version
    "slack_messenger"           = var.slack_messenger_version
    "quality_checker"           = var.quality_checker_version
  }
}
