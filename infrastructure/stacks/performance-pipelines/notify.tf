resource "aws_sns_topic" "pipeline_notification_topic" {
  name = var.pipeline_topic_name
}

resource "aws_codestarnotifications_notification_rule" "stress_test_pipeline_notifications" {
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = "${var.project_id}-${var.environment}-stress-test-pipeline-notification"
  resource = aws_codepipeline.stress_test_codepipeline.arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_nonprod}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}

resource "aws_codestarnotifications_notification_rule" "load_test_pipeline_notifications" {
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = "${var.project_id}-${var.environment}-load-test-pipeline-notification"
  resource = aws_codepipeline.load_test_codepipeline.arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_nonprod}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}
