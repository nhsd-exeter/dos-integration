# ==============================================================================
# Outputs

output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}
output "vpc_arn" {
  description = "The ARN of the VPC"
  value       = module.vpc.vpc_arn
}
output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}
output "vpc_public_subnets" {
  description = "The list of public subnets inside the VPC"
  value       = module.vpc.public_subnets
}
output "vpc_private_subnets" {
  description = "The list of private subnets inside the VPC"
  value       = module.vpc.private_subnets
}
output "vpc_intra_subnets" {
  description = "The list of internal subnets inside the VPC"
  value       = module.vpc.intra_subnets
}
output "default_security_group_id" {
  description = "The ID of the security group created by default on VPC creation"
  value       = module.vpc.default_security_group_id
}
