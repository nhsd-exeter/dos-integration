#tfsec:ignore:aws-sns-enable-topic-encryption
resource "aws_sns_topic" "pipeline_notification_topic" {
  name              = var.pipeline_topic_name
  kms_master_key_id = "alias/aws/sns"
}


resource "aws_codestarnotifications_notification_rule" "development_pipeline_notfication_rule" {
  count          = var.environment == "dev" ? 1 : 0
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = var.pipeline_notification_name
  resource = aws_codepipeline.development_pipeline[0].arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}

# resource "aws_codestarnotifications_notification_rule" "cicd_blue_green_deployment_pipeline_commits" {
#   count          = var.environment == "di-618" ? 1 : 0
#   detail_type    = "BASIC"
#   event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

#   name     = var.pipeline_notification_name
#   resource = aws_codepipeline.cicd_blue_green_deployment_pipeline[0].arn

#   target {
#     type    = "AWSChatbotSlack"
#     address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
#   }
# }
