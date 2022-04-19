resource "aws_appconfig_application" "di_lambdas" {
  name        = "${var.project_id}-${var.environment}-lambda-app-config"
  description = "Example AppConfig Application"
}

resource "aws_appconfig_configuration_profile" "event_processor" {
  application_id = aws_appconfig_application.di_lambdas.id
  name           = "event-processor"
  description    = "AppConfig Configuration Profile for Event Processor"
  location_uri   = "hosted"
  type           = "AWS.Freeform"
}

resource "aws_appconfig_environment" "lambdas_environment" {
  name           = var.environment
  description    = "AppConfig Environment for ${var.environment}"
  application_id = aws_appconfig_application.di_lambdas.id
}

resource "aws_appconfig_hosted_configuration_version" "event_processor_version" {
  application_id           = aws_appconfig_application.di_lambdas.id
  configuration_profile_id = aws_appconfig_configuration_profile.event_processor.configuration_profile_id
  description              = "AppConfig Hosted Configuration Version for Event Processor"
  content_type             = "application/json"

  content = jsonencode({
    "accepted_org_types" : {
      "default" : false,
      "rules" : {
        "org_type_in_list" : {
          "when_match" : true,
          "conditions" : [
            {
              "action" : "KEY_IN_VALUE",
              "key" : "org_type",
              "value" : var.accepted_org_types
            }
          ]
        }
      }
    }
    }
  )
}

resource "aws_appconfig_deployment" "deployment" {
  application_id           = aws_appconfig_application.di_lambdas.id
  configuration_profile_id = aws_appconfig_configuration_profile.event_processor.configuration_profile_id
  configuration_version    = aws_appconfig_hosted_configuration_version.event_processor_version.version_number
  deployment_strategy_id   = "AppConfig.AllAtOnce"
  description              = "AppConfig Deployment for Event Processor"
  environment_id           = aws_appconfig_environment.lambdas_environment.environment_id
}
