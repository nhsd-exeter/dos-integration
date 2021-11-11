data "terraform_remote_state" "route53" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.vpc_terraform_state_key
    region = var.aws_region
  }
}

data "aws_route53_zone" "k8s_route53_zone" {
  name = var.terraform_networking_route53_zone_name
}

# Find a certificate that is issued
data "aws_acm_certificate" "issued" {
  domain   = "*.${var.terraform_networking_route53_zone_name}"
  statuses = ["ISSUED"]
}
data "aws_api_gateway_rest_api" "restapi" {
  name = "${var.profile}-${var.programme}-${var.team_id}"
}

