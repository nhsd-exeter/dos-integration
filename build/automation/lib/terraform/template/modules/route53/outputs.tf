# ==============================================================================
# Outputs

output "this_route53_zone_zone_id" {
  description = "Zone ID of Route53 zone"
  value       = module.route53-zone.this_route53_zone_zone_id
}
output "this_route53_zone_name_servers" {
  description = "Name servers of Route53 zone"
  value       = module.route53-zone.this_route53_zone_name_servers
}
