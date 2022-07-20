#tfsec:ignore:aws-sns-enable-topic-encryption
resource "aws_sns_topic" "pipeline_notification_topic" {
  name              = var.pipeline_topic_name
  kms_master_key_id = "alias/aws/sns"
}


resource "aws_codestarnotifications_notification_rule" "commits" {
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = var.pipeline_notification_name
  resource = aws_codepipeline.codepipeline.arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}
