# ##############
# # IAM
# ##############

data "aws_iam_role" "pipeline_role" {
  name = "UECDoSINTPipelineRole"
}

# ##############
# # VPC
# ##############

data "aws_vpc" "texas_mgmt_vpc" {
  tags = {
    "Name" = var.mgmt_vpc_name
  }
}
data "aws_subnet" "vpc_subnet_one" {
  filter {
    name   = "tag:Name"
    values = ["${var.mgmt_vpc_name}-private-${var.aws_region}a"]
  }
}

data "aws_subnet" "vpc_subnet_two" {
  filter {
    name   = "tag:Name"
    values = ["${var.mgmt_vpc_name}-private-${var.aws_region}b"]
  }
}

data "aws_subnet" "vpc_subnet_three" {
  filter {
    name   = "tag:Name"
    values = ["${var.mgmt_vpc_name}-private-${var.aws_region}c"]
  }
}
