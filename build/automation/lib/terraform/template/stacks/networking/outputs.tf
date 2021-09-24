# ==============================================================================
# Outputs

# --------------------------------------
# vpn

output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_id
}
output "vpc_arn" {
  description = "The ARN of the VPC"
  value       = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_arn
}
output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_cidr_block
}
output "vpc_public_subnets" {
  description = "The list of public subnets inside the VPC"
  value       = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_public_subnets
}
output "vpc_private_subnets" {
  description = "The list of private subnets inside the VPC"
  value       = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_private_subnets
}
output "vpc_intra_subnets" {
  description = "The list of internal subnets inside the VPC"
  value       = module.NAME_TEMPLATE_TO_REPLACE-vpc.vpc_intra_subnets
}
output "vpc_default_security_group_id" {
  description = "The ID of the security group created by default on VPC creation"
  value       = module.NAME_TEMPLATE_TO_REPLACE-vpc.default_security_group_id
}

# --------------------------------------
# alb

output "alb_id" {
  description = "The ID and ARN of the load balancer we created"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_id
}
output "alb_arn" {
  description = "The ID and ARN of the load balancer we created"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_arn
}
output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_dns_name
}
output "alb_arn_suffix" {
  description = "ARN suffix of our load balancer - can be used with CloudWatch"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_arn_suffix
}
output "alb_zone_id" {
  description = "The zone_id of the load balancer to assist with creating DNS records"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.this_lb_zone_id
}
output "alb_https_listener_arns" {
  description = "The ARNs of the HTTPS load balancer listeners created"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.https_listener_arns
}
output "alb_https_listener_ids" {
  description = "The IDs of the load balancer listeners created"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.https_listener_ids
}
output "alb_http_tcp_listener_arns" {
  description = "The ARN of the TCP and HTTP load balancer listeners created"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.http_tcp_listener_arns
}
output "alb_http_tcp_listener_ids" {
  description = "The IDs of the TCP and HTTP load balancer listeners created"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.http_tcp_listener_ids
}
output "alb_target_group_arns" {
  description = "ARNs of the target groups. Useful for passing to your Auto Scaling group"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.target_group_arns
}
output "alb_target_group_arn_suffixes" {
  description = "ARN suffixes of our target groups - can be used with CloudWatch"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.target_group_arn_suffixes
}
output "alb_target_group_names" {
  description = "Name of the target group. Useful for passing to your CodeDeploy Deployment Group"
  value       = module.NAME_TEMPLATE_TO_REPLACE-alb.target_group_names
}

# --------------------------------------
# acm

output "acm_certificate_arn" {
  description = "The ARN of the certificate"
  value       = module.NAME_TEMPLATE_TO_REPLACE-acm.this_acm_certificate_arn
}
output "acm_certificate_domain_validation_options" {
  description = "A list of attributes to feed into other resources to complete certificate validation. Can have more than one element, e.g. if SANs are defined. Only set if DNS-validation was used"
  value       = module.NAME_TEMPLATE_TO_REPLACE-acm.this_acm_certificate_domain_validation_options
}
output "acm_certificate_validation_emails" {
  description = "A list of addresses that received a validation E-Mail. Only set if EMAIL-validation was used"
  value       = module.NAME_TEMPLATE_TO_REPLACE-acm.this_acm_certificate_validation_emails
}
output "acm_validation_route53_record_fqdns" {
  description = "List of FQDNs built using the zone domain and name"
  value       = module.NAME_TEMPLATE_TO_REPLACE-acm.validation_route53_record_fqdns
}
output "acm_distinct_domain_names" {
  description = "List of distinct domains names used for the validation"
  value       = module.NAME_TEMPLATE_TO_REPLACE-acm.distinct_domain_names
}
output "acm_validation_domains" {
  description = "List of distinct domain validation options. This is useful if subject alternative names contain wildcards"
  value       = module.NAME_TEMPLATE_TO_REPLACE-acm.validation_domains
}

# --------------------------------------
# route53

output "route53_zone_zone_id" {
  description = "The zone ID of Route53 zone"
  value       = module.NAME_TEMPLATE_TO_REPLACE-route53.this_route53_zone_zone_id
}
output "route53_zone_name_servers" {
  description = "The name servers of Route53 zone"
  value       = module.NAME_TEMPLATE_TO_REPLACE-route53.this_route53_zone_name_servers
}

# --------------------------------------
# ecs

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.NAME_TEMPLATE_TO_REPLACE-ecs.this_ecs_cluster_arn
}
output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = module.NAME_TEMPLATE_TO_REPLACE-ecs.this_ecs_cluster_id
}
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.NAME_TEMPLATE_TO_REPLACE-ecs.this_ecs_cluster_name
}
