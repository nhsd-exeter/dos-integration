module "route53-zone" {
  source  = "terraform-aws-modules/route53/aws//modules/zones"
  version = "1.5.0"

  zones = {
    "${var.zone_name}" = {
      comment = "This is a default zone"
      tags    = var.context.tags
    }
  }
}

module "route53-records" {
  source  = "terraform-aws-modules/route53/aws//modules/records"
  version = "1.5.0"

  depends_on = [module.route53-zone]
  zone_name  = keys(module.route53-zone.this_route53_zone_zone_id)[0]

  records = var.records
}
