data "terraform_remote_state" "route53" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.route53_terraform_state_key
    region = var.aws_region
  }
}
data "aws_acm_certificate" "issued" {
  domain   = "*.${var.texas_hosted_zone}"
  statuses = ["ISSUED"]
}
data "aws_api_gateway_rest_api" "change_request_receiver" {
  name = var.change_request_receiver_api_name
}
