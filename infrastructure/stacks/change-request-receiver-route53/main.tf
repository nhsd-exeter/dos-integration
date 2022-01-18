resource "aws_api_gateway_domain_name" "change_request_receiver_api_gateway_domain_name" {
  regional_certificate_arn = data.aws_acm_certificate.issued.arn
  domain_name              = "${var.change_request_receiver_subdomain_name}.${var.texas_hosted_zone}"
  security_policy          = "TLS_1_2"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
resource "aws_route53_record" "change_request_receiver_api_endpoint" {
  name    = "${var.change_request_receiver_subdomain_name}.${var.texas_hosted_zone}"
  type    = "A"
  zone_id = data.terraform_remote_state.route53.outputs.dns_zone_id
  alias {
    name                   = aws_api_gateway_domain_name.change_request_receiver_api_gateway_domain_name.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.change_request_receiver_api_gateway_domain_name.regional_zone_id
    evaluate_target_health = true
  }
}
resource "aws_api_gateway_base_path_mapping" "change_request_receiver_api_mapping" {
  api_id      = data.aws_api_gateway_rest_api.change_request_receiver.id
  stage_name  = var.environment
  domain_name = "${var.change_request_receiver_subdomain_name}.${var.texas_hosted_zone}"
}
