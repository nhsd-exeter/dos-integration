resource "aws_api_gateway_base_path_mapping" "uec_dos_integration_api_mapping" {
  api_id      = aws_api_gateway_rest_api.di_endpoint.id
  stage_name  = var.shared_environment
  domain_name = "${var.dos_integration_sub_domain_name}.${var.texas_hosted_zone}"
  depends_on  = [aws_api_gateway_stage.di_endpoint_stage]
}

resource "aws_api_gateway_domain_name" "api_gateway_domain_name" {
  regional_certificate_arn = data.aws_acm_certificate.issued.arn
  domain_name              = "${var.dos_integration_sub_domain_name}.${var.texas_hosted_zone}"
  security_policy          = "TLS_1_2"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  tags = {
    "PublicFacing" = "Yes"
  }
}

resource "aws_route53_record" "uec_dos_integration_api_endpoint" {
  name    = "${var.dos_integration_sub_domain_name}.${var.texas_hosted_zone}"
  type    = "A"
  zone_id = data.aws_route53_zone.texas_hosted_zone.zone_id
  alias {
    name                   = aws_api_gateway_domain_name.api_gateway_domain_name.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api_gateway_domain_name.regional_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_health_check" "di_endpoint_health_check" {
  fqdn              = "${var.dos_integration_sub_domain_name}.${var.texas_hosted_zone}"
  port              = 443
  type              = "TCP"
  failure_threshold = "5"
  request_interval  = "30"
  tags = {
    Name = "${var.project_id}-${var.shared_environment}-di-endpoint-health-check"
  }

  depends_on = [
    aws_route53_record.uec_dos_integration_api_endpoint
  ]
}
