#tfsec:ignore:aws-sns-topic-encryption-use-cmk
resource "aws_sns_topic" "pipeline_notification_topic" {
  name              = var.pipeline_topic_name
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_codestarnotifications_notification_rule" "development_pipeline_notfication_rule" {
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = var.pipeline_notification_name
  resource = aws_codepipeline.development_pipeline.arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}

resource "aws_codestarnotifications_notification_rule" "cicd_blue_green_deployment_pipeline" {
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = var.cicd_blue_green_deployment_pipeline_nofitication_name
  resource = aws_codepipeline.cicd_blue_green_deployment_pipeline.arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}

resource "aws_codestarnotifications_notification_rule" "cicd_shared_deployment_pipeline" {
  detail_type    = "BASIC"
  event_type_ids = ["codepipeline-pipeline-pipeline-execution-started", "codepipeline-pipeline-pipeline-execution-failed", "codepipeline-pipeline-pipeline-execution-succeeded"]

  name     = var.cicd_shared_resources_deployment_pipeline_nofitication_name
  resource = aws_codepipeline.cicd_shared_resources_deployment_pipeline.arn

  target {
    type    = "AWSChatbotSlack"
    address = "arn:aws:chatbot::${var.aws_account_id_mgmt}:chat-configuration/slack-channel/${var.pipeline_chatbot_channel}"
  }
}
