# ################################
# # Route53 and APIGateway Domain
# ################################
resource "aws_api_gateway_domain_name" "api_gateway_domain_name" {
  regional_certificate_arn = data.aws_acm_certificate.issued.arn
  domain_name              = "${var.dos_api_gateway_name}.${var.texas_hosted_zone}"
  security_policy          = "TLS_1_2"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
resource "aws_route53_record" "uec_dos_integration_api_endpoint" {
  name    = "${var.dos_api_gateway_name}.${var.texas_hosted_zone}"
  type    = "A"
  zone_id = data.terraform_remote_state.route53.outputs.dns_zone_id
  alias {
    name                   = aws_api_gateway_domain_name.api_gateway_domain_name.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api_gateway_domain_name.regional_zone_id
    evaluate_target_health = true
  }
}
resource "aws_api_gateway_base_path_mapping" "uec-dos-integration_api_mapping" {
  api_id      = aws_api_gateway_rest_api.dos_api_gateway.id
  stage_name  = var.dos_api_gateway_stage
  domain_name = "${var.dos_api_gateway_name}.${var.texas_hosted_zone}"
  depends_on = [
    aws_api_gateway_stage.dos_api_gateway_stage,
  ]
}
