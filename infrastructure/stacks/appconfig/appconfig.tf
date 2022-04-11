resource "aws_appconfig_application" "di_lambdas" {
  name        = "${var.project_id}-${var.environment}-lambda-app-config"
  description = "Example AppConfig Application"
}

resource "aws_appconfig_configuration_profile" "event_processor" {
  application_id = aws_appconfig_application.di_lambdas.id
  name           = "${var.project_id}-${var.environment}-event-processor-profile"
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
    is_pharmacy_accepted : {
      default : var.is_pharmacy_accepted
    },
    is_dentist_accepted : {
      default : var.is_dentist_accepted
    }
  })
}
