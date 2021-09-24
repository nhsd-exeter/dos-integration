module "security-group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "3.17.0"
  tags    = var.context.tags

  name        = var.name
  description = var.description
  vpc_id      = var.vpc_id

  ingress_rules                         = var.ingress_rules
  ingress_with_self                     = var.ingress_with_self
  ingress_with_cidr_blocks              = var.ingress_with_cidr_blocks
  ingress_with_ipv6_cidr_blocks         = var.ingress_with_ipv6_cidr_blocks
  ingress_with_source_security_group_id = var.ingress_with_source_security_group_id
  ingress_cidr_blocks                   = var.ingress_cidr_blocks
  ingress_ipv6_cidr_blocks              = var.ingress_ipv6_cidr_blocks
  ingress_prefix_list_ids               = var.ingress_prefix_list_ids
  egress_rules                          = var.egress_rules
  egress_with_self                      = var.egress_with_self
  egress_with_cidr_blocks               = var.egress_with_cidr_blocks
  egress_with_ipv6_cidr_blocks          = var.egress_with_ipv6_cidr_blocks
  egress_with_source_security_group_id  = var.egress_with_source_security_group_id
  egress_cidr_blocks                    = var.egress_cidr_blocks
  egress_ipv6_cidr_blocks               = var.egress_ipv6_cidr_blocks
  egress_prefix_list_ids                = var.egress_prefix_list_ids
}
