resource "aws_api_gateway_method_response" "response_200" {
  http_method = aws_api_gateway_method.di_endpoint_method.http_method
  resource_id = aws_api_gateway_resource.di_endpoint_change_event_path.id
  rest_api_id = aws_api_gateway_rest_api.di_endpoint.id
  status_code = "200"
  response_parameters = {
    "method.response.header.Cache-control"             = true
    "method.response.header.Pragma"                    = true
    "method.response.header.Strict-Transport-Security" = true
    "method.response.header.X-Frame-Options"           = true
    "method.response.header.X-Content-Type-Option"     = true
    "method.response.header.X-Content-Type-Options"    = true
    "method.response.header.Content-Security-Policy"   = true
  }
  response_models = {
    "application/json" = aws_api_gateway_model.default_model.name
  }
}

resource "aws_api_gateway_method_response" "response_400" {
  http_method = aws_api_gateway_method.di_endpoint_method.http_method
  resource_id = aws_api_gateway_resource.di_endpoint_change_event_path.id
  rest_api_id = aws_api_gateway_rest_api.di_endpoint.id
  status_code = "400"
  response_parameters = {
    "method.response.header.Cache-control"             = true
    "method.response.header.Pragma"                    = true
    "method.response.header.Strict-Transport-Security" = true
    "method.response.header.X-Frame-Options"           = true
    "method.response.header.X-Content-Type-Option"     = true
    "method.response.header.X-Content-Type-Options"    = true
    "method.response.header.Content-Security-Policy"   = true
  }
  response_models = {
    "application/json" = aws_api_gateway_model.default_model.name
  }
}

resource "aws_api_gateway_method_response" "response_500" {
  http_method = aws_api_gateway_method.di_endpoint_method.http_method
  resource_id = aws_api_gateway_resource.di_endpoint_change_event_path.id
  rest_api_id = aws_api_gateway_rest_api.di_endpoint.id
  status_code = "500"
  response_parameters = {
    "method.response.header.Cache-control"             = true
    "method.response.header.Pragma"                    = true
    "method.response.header.Strict-Transport-Security" = true
    "method.response.header.X-Frame-Options"           = true
    "method.response.header.X-Content-Type-Option"     = true
    "method.response.header.X-Content-Type-Options"    = true
    "method.response.header.Content-Security-Policy"   = true
  }
  response_models = {
    "application/json" = aws_api_gateway_model.default_model.name
  }
}

resource "aws_api_gateway_integration_response" "di_endpoint_integration_success_response" {
  http_method        = aws_api_gateway_method.di_endpoint_method.http_method
  resource_id        = aws_api_gateway_resource.di_endpoint_change_event_path.id
  rest_api_id        = aws_api_gateway_rest_api.di_endpoint.id
  status_code        = aws_api_gateway_method_response.response_200.status_code
  selection_pattern  = "^2[0-9][0-9]"
  response_templates = ({ "application/json" : jsonencode({ "Message" : "Change event received" }) })
  response_parameters = {
    "method.response.header.Cache-control"             = "'no-cache'"
    "method.response.header.Pragma"                    = "'no-store'"
    "method.response.header.Strict-Transport-Security" = "'max-age=31536000; includeSubDomains'"
    "method.response.header.X-Frame-Options"           = "'DENY'"
    "method.response.header.X-Content-Type-Option"     = "'nosniff'"
    "method.response.header.X-Content-Type-Options"    = "'nosniff'"
    "method.response.header.Content-Security-Policy"   = "'default-src 'self''"
  }

  depends_on = [
    aws_api_gateway_method_response.response_200,
    aws_api_gateway_integration.di_endpoint_integration,
    aws_api_gateway_resource.di_endpoint_change_event_path,
    aws_api_gateway_method.di_endpoint_method,
  ]
}

resource "aws_api_gateway_integration_response" "response_400" {
  http_method        = aws_api_gateway_method.di_endpoint_method.http_method
  resource_id        = aws_api_gateway_resource.di_endpoint_change_event_path.id
  rest_api_id        = aws_api_gateway_rest_api.di_endpoint.id
  status_code        = aws_api_gateway_method_response.response_400.status_code
  selection_pattern  = "^4[0-9][0-9]"
  response_templates = ({ "application/json" : jsonencode({ "Message" : "Bad Request" }) })
  response_parameters = {
    "method.response.header.Cache-control"             = "'no-cache'"
    "method.response.header.Pragma"                    = "'no-store'"
    "method.response.header.Strict-Transport-Security" = "'max-age=31536000; includeSubDomains'"
    "method.response.header.X-Frame-Options"           = "'DENY'"
    "method.response.header.X-Content-Type-Option"     = "'nosniff'"
    "method.response.header.X-Content-Type-Options"    = "'nosniff'"
    "method.response.header.Content-Security-Policy"   = "'default-src 'self''"
  }

  depends_on = [
    aws_api_gateway_method_response.response_400,
    aws_api_gateway_integration.di_endpoint_integration,
    aws_api_gateway_resource.di_endpoint_change_event_path,
    aws_api_gateway_method.di_endpoint_method,
  ]
}

resource "aws_api_gateway_integration_response" "response_500" {
  http_method        = aws_api_gateway_method.di_endpoint_method.http_method
  resource_id        = aws_api_gateway_resource.di_endpoint_change_event_path.id
  rest_api_id        = aws_api_gateway_rest_api.di_endpoint.id
  status_code        = aws_api_gateway_method_response.response_500.status_code
  selection_pattern  = "^5[0-9][0-9]"
  response_templates = ({ "application/json" : jsonencode({ "Message" : "Server Error" }) })
  response_parameters = {
    "method.response.header.Cache-control"             = "'no-cache'"
    "method.response.header.Pragma"                    = "'no-store'"
    "method.response.header.Strict-Transport-Security" = "'max-age=31536000; includeSubDomains'"
    "method.response.header.X-Frame-Options"           = "'DENY'"
    "method.response.header.X-Content-Type-Option"     = "'nosniff'"
    "method.response.header.X-Content-Type-Options"    = "'nosniff'"
    "method.response.header.Content-Security-Policy"   = "'default-src 'self''"
  }

  depends_on = [
    aws_api_gateway_method_response.response_500,
    aws_api_gateway_integration.di_endpoint_integration,
    aws_api_gateway_resource.di_endpoint_change_event_path,
    aws_api_gateway_method.di_endpoint_method,
  ]
}

resource "aws_api_gateway_gateway_response" "access_denied_403_gateway_response" {
  rest_api_id        = aws_api_gateway_rest_api.di_endpoint.id
  status_code        = "403"
  response_type      = "ACCESS_DENIED"
  response_templates = ({ "application/json" : jsonencode({ "Message" : "Access Denied, please contact the development team for assistance" }) })

  depends_on = [
    aws_api_gateway_integration.di_endpoint_integration,
    aws_api_gateway_resource.di_endpoint_change_event_path,
    aws_api_gateway_method.di_endpoint_method,
  ]
}
