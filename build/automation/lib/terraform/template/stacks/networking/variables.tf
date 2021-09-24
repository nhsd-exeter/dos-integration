# ==============================================================================
# User variables

variable "terraform_networking_vpc_name" { description = "The VPC network name" }
variable "terraform_networking_vpc_id" { description = "The VPC network ID used to define the CIDR address block, i.e. 10.vpc_id.0.0/16" }
variable "terraform_networking_route53_zone_name" { description = "The Route53 zone name" }
