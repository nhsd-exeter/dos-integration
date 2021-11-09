# ############################
# # Route53 and APIGateway
# ############################
resource "aws_api_gateway_domain_name" "api_gateway_domain_name" {
  certificate_arn = data.aws_acm_certificate.issued.arn
  domain_name     = "${var.dos_integration_sub_domain_name}.${var.terraform_networking_route53_zone_name}"
  security_policy = "TLS_1_2"
}

resource "aws_api_gateway_base_path_mapping" "uec-dos-integration_api_mapping" {
  api_id      = data.aws_api_gateway_rest_api.restapi.id
  stage_name  = var.profile
  domain_name = "${var.dos_integration_sub_domain_name}.${var.terraform_networking_route53_zone_name}"
}

resource "aws_route53_record" "uec-dos-integration_api_endpoint" {
  name    = "${var.dos_integration_sub_domain_name}.${var.terraform_networking_route53_zone_name}"
  type    = "A"
  zone_id = data.aws_route53_zone.k8s_route53_zone.zone_id
  alias {
    name                   = aws_api_gateway_domain_name.api_gateway_domain_name.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.api_gateway_domain_name.cloudfront_zone_id
    evaluate_target_health = true
  }
}


