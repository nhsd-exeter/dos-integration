module "eventbridge" {
  source = "terraform-aws-modules/eventbridge/aws"

  rules = {
    orders = {
      description = "Capture all events from event processor"
      event_pattern = jsonencode({ "source" : ["aws.lambda"],
        "resources" : ["${data.aws_lambda_function.event_processor.arn}"]
      })
      enabled = true
    }
  }
}
targets = {
  change_request = [
    {
      name            = "sending change request to dos api gateway "
      destination     = "change_request"
      arn             = ""
      attach_role_arn = true
    }

  ]
}
connections = {
  change_request = {
    authorization_type = "BASIC"
    auth_parameters = {

      basic = {
        username = jsondecode(data.aws_secretsmanager_secret_version.change_request_username.secret_string)[var.username_key]
        password = jsondecode(data.aws_secretsmanager_secret_version.change_request_password.secret_string)[var.password_key]
      }

      invocation_http_parameters = {

        header = [{
          key             = "Content-Type"
          value           = "application/json"
          is_value_secret = false
          }
      ] }
    }
  }
  api_destinations = {
    change_request = {
      description                      = "dos api gateway change request endpoint"
      invocation_endpoint              = var.change_request_endpoint
      http_method                      = "POST"
      invocation_rate_limit_per_second = 3
    }
  }
}
