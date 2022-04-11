resource "aws_appconfig_deployment" "deployment" {
  application_id           = aws_appconfig_application.di_lambdas.id
  configuration_profile_id = aws_appconfig_configuration_profile.event_processor.configuration_profile_id
  configuration_version    = aws_appconfig_hosted_configuration_version.event_processor_version.version_number
  deployment_strategy_id   = aws_appconfig_deployment_strategy.deployment_strategy.id
  description              = "AppConfig Deployment for Event Processor"
  environment_id           = aws_appconfig_environment.lambdas_environment.environment_id
}

resource "aws_appconfig_deployment_strategy" "deployment_strategy" {
  name                           = "${var.project_id}-${var.environment}-deployment-strategy"
  description                    = "AppConfig Deployment Strategy for Event Processor"
  deployment_duration_in_minutes = 0
  final_bake_time_in_minutes     = 0
  growth_factor                  = 100
  growth_type                    = "LINEAR"
  replicate_to                   = "NONE"
}
