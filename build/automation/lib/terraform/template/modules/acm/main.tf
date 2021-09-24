module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "2.12.0"
  tags    = var.context.tags

  zone_id                   = var.route53_zone_id
  domain_name               = var.cert_domain_name
  subject_alternative_names = var.cert_subject_alternative_names
  wait_for_validation       = false
}
