module "NAME_TEMPLATE_TO_REPLACE-vpc" {
  source  = "../../modules/vpc"
  context = local.context

  vpc_name = var.terraform_networking_vpc_name
  vpc_id   = var.terraform_networking_vpc_id
}

module "NAME_TEMPLATE_TO_REPLACE-alb" {
  source  = "../../modules/alb"
  context = local.context

  name            = "default-lb"
  vpc_id          = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_id
  subnets         = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_public_subnets
  certificate_arn = module.NAME_TEMPLATE_TO_REPLACE-acm.this_acm_certificate_arn
}

module "NAME_TEMPLATE_TO_REPLACE-acm" {
  source  = "../../modules/acm"
  context = local.context

  cert_domain_name               = var.terraform_networking_route53_zone_name
  cert_subject_alternative_names = ["*.${var.terraform_networking_route53_zone_name}"]
  route53_zone_id                = module.NAME_TEMPLATE_TO_REPLACE-route53.this_route53_zone_zone_id[var.terraform_networking_route53_zone_name]
}

module "NAME_TEMPLATE_TO_REPLACE-route53" {
  source  = "../../modules/route53"
  context = local.context

  zone_name = var.terraform_networking_route53_zone_name
  records = [
    {
      name = "www"
      type = "A"
      alias = {
        name                   = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_dns_name
        zone_id                = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_zone_id
        evaluate_target_health = true
      }
    },
    {
      name = ""
      type = "A"
      alias = {
        name                   = "www.${module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_dns_name}"
        zone_id                = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_zone_id
        evaluate_target_health = true
      }
    }
  ]
}

module "NAME_TEMPLATE_TO_REPLACE-ecs" {
  source  = "../../modules/ecs"
  context = local.context

  name = "default-cluster"
}

module "NAME_TEMPLATE_TO_REPLACE-appmesh" {
  source  = "../../modules/appmesh"
  context = local.context

  name = "default-mesh"
}

# module "NAME_TEMPLATE_TO_REPLACE-vpn" {
#   source  = "../../modules/vpn"
#   context = local.context
#
#   name = "vpn"
# }
