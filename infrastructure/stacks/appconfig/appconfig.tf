resource "aws_appconfig_application" "di_lambdas" {
  name        = "${var.project_id}-${var.environment}-lambda-app-config"
  description = "DoS Integration AppConfig Application"
}

resource "aws_appconfig_environment" "lambdas_environment" {
  name           = var.environment
  description    = "AppConfig Environment for ${var.environment}"
  application_id = aws_appconfig_application.di_lambdas.id
}

resource "aws_appconfig_configuration_profile" "ingest_change_event" {
  application_id = aws_appconfig_application.di_lambdas.id
  name           = "ingest-change-event"
  description    = "AppConfig Configuration Profile for Ingest Change Event lambda"
  location_uri   = "hosted"
  type           = "AWS.Freeform"
}

resource "aws_appconfig_hosted_configuration_version" "ingest_change_event_version" {
  application_id           = aws_appconfig_application.di_lambdas.id
  configuration_profile_id = aws_appconfig_configuration_profile.ingest_change_event.configuration_profile_id
  description              = "AppConfig Hosted Configuration Version for Ingest Change Event lambda"
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

resource "aws_appconfig_deployment" "ingest_change_event_deployment" {
  application_id           = aws_appconfig_application.di_lambdas.id
  configuration_profile_id = aws_appconfig_configuration_profile.ingest_change_event.configuration_profile_id
  configuration_version    = aws_appconfig_hosted_configuration_version.ingest_change_event_version.version_number
  deployment_strategy_id   = "AppConfig.AllAtOnce"
  description              = "AppConfig Deployment for ${var.environment} Ingest Change Event"
  environment_id           = aws_appconfig_environment.lambdas_environment.environment_id
}

resource "aws_appconfig_configuration_profile" "service_matcher" {
  application_id = aws_appconfig_application.di_lambdas.id
  name           = "service-matcher"
  description    = "AppConfig Configuration Profile for Service Matcher lambda"
  location_uri   = "hosted"
  type           = "AWS.Freeform"
}

resource "aws_appconfig_hosted_configuration_version" "service_matcher_version" {
  application_id           = aws_appconfig_application.di_lambdas.id
  configuration_profile_id = aws_appconfig_configuration_profile.service_matcher.configuration_profile_id
  description              = "AppConfig Hosted Configuration Version for Service Matcher lambda"
  content_type             = "application/json"

  content = jsonencode({
    "accepted_service_types" : {
      "default" : false,
      "rules" : {
        "active_service_types" : {
          "when_match" : true,
          "conditions" : [
            {
              "action" : "KEY_IN_VALUE",
              "key" : "service_type_ids",
              "value" : [13, 131, 132, 134, 137]
            }
          ]
          }, "active_closed_commissioning_service_types" : {
          "when_match" : true,
          "conditions" : [
            {
              "action" : "KEY_IN_VALUE",
              "key" : "service_type_ids",
              "value" : []
            }
          ]
        }
      }
    }
    }
  )
}

resource "aws_appconfig_deployment" "service_matcher_deployment" {
  application_id           = aws_appconfig_application.di_lambdas.id
  configuration_profile_id = aws_appconfig_configuration_profile.service_matcher.configuration_profile_id
  configuration_version    = aws_appconfig_hosted_configuration_version.service_matcher_version.version_number
  deployment_strategy_id   = "AppConfig.AllAtOnce"
  description              = "AppConfig Deployment for ${var.environment} Service Matcher"
  environment_id           = aws_appconfig_environment.lambdas_environment.environment_id
}
