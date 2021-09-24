module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.64.0"
  tags    = var.context.tags

  name = var.vpc_name
  cidr = "10.${var.vpc_id}.0.0/16"

  public_subnets  = ["10.${var.vpc_id}.192.0/21", "10.${var.vpc_id}.200.0/21", "10.${var.vpc_id}.208.0/21"]
  private_subnets = ["10.${var.vpc_id}.0.0/19", "10.${var.vpc_id}.32.0/19", "10.${var.vpc_id}.64.0/19"]
  intra_subnets   = ["10.${var.vpc_id}.128.0/20", "10.${var.vpc_id}.144.0/20", "10.${var.vpc_id}.160.0/20"]
  azs             = [data.aws_availability_zones.available.names[0], data.aws_availability_zones.available.names[1], data.aws_availability_zones.available.names[2]]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true
  enable_dns_hostnames   = true
  enable_dns_support     = true

  enable_flow_log                                 = true
  create_flow_log_cloudwatch_iam_role             = true
  create_flow_log_cloudwatch_log_group            = true
  flow_log_max_aggregation_interval               = 60
  flow_log_cloudwatch_log_group_retention_in_days = 7
}

resource "aws_network_acl" "public_subnets_network_acl" {
  vpc_id     = module.vpc.vpc_id
  subnet_ids = flatten([module.vpc.public_subnets])
  tags       = var.context.tags

  # Allow ingress traffic on specified ports only from the internet
  dynamic "ingress" {
    for_each = var.public_subnet_port_rules
    content {
      rule_no    = ingress.key
      protocol   = "tcp"
      action     = "allow"
      from_port  = ingress.value
      to_port    = ingress.value
      cidr_block = "0.0.0.0/0"
    }
  }
  # Ephemeral ports
  ingress {
    protocol   = "tcp"
    rule_no    = 999
    action     = "allow"
    from_port  = 1024
    to_port    = 65535
    cidr_block = "0.0.0.0/0"
  }
  # Outbound traffic
  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    from_port  = 0
    to_port    = 0
    cidr_block = "0.0.0.0/0"
  }
}

resource "aws_network_acl" "private_subnets_network_acl" {
  vpc_id     = module.vpc.vpc_id
  subnet_ids = flatten([module.vpc.private_subnets])
  tags       = var.context.tags

  # Allow ingress traffic on specified ports only from the public subnet
  dynamic "ingress" {
    for_each = var.private_subnet_port_rules
    content {
      rule_no    = ingress.key
      protocol   = "tcp"
      action     = "allow"
      from_port  = ingress.value
      to_port    = ingress.value
      cidr_block = "10.${var.vpc_id}.192.0/19"
    }
  }
  # Ephemeral ports
  ingress {
    protocol   = "tcp"
    rule_no    = 999
    action     = "allow"
    from_port  = 1024
    to_port    = 65535
    cidr_block = "0.0.0.0/0"
  }
  # Outbound traffic
  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    from_port  = 0
    to_port    = 0
    cidr_block = "0.0.0.0/0"
  }
}

resource "aws_network_acl" "intra_subnets_network_acl" {
  vpc_id     = module.vpc.vpc_id
  subnet_ids = flatten([module.vpc.intra_subnets])
  tags       = var.context.tags

  # Allow ingress traffic on specified ports only from the private subnet
  dynamic "ingress" {
    for_each = var.internal_subnet_port_rules
    content {
      rule_no    = ingress.key
      protocol   = "tcp"
      action     = "allow"
      from_port  = ingress.value
      to_port    = ingress.value
      cidr_block = "10.${var.vpc_id}.0.0/17"
    }
  }
  # Ephemeral ports
  ingress {
    protocol   = "tcp"
    rule_no    = 999
    action     = "allow"
    from_port  = 1024
    to_port    = 65535
    cidr_block = "0.0.0.0/0"
  }
}
