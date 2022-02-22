data "template_file" "unit_tests_buildspec" {
  template = file("unit-tests-buildspec.yml")
}

data "template_file" "build_buildspec" {
  template = file("build-buildspec.yml")
}

data "template_file" "deploy_buildspec" {
  template = file("deploy-buildspec.yml")
}


data "template_file" "integration_tests_buildspec" {
  template = file("integration-tests-buildspec.yml")
}

data "aws_kms_key" "singing_key" {
  key_id = "alias/${var.test_signing_key_alias}"
}

data "aws_security_group" "lambdagroup" {
  name = var.lambda_security_group_name
}


data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = [var.aws_vpc_name]
  }
}

data "aws_subnet_ids" "selected" {
  vpc_id = data.aws_vpc.vpc.id
  filter {
    name = "tag:Name"
    values = ["${var.aws_vpc_name}-private-${var.aws_region}a",
      "${var.aws_vpc_name}-private-${var.aws_region}b",
    "${var.aws_vpc_name}-private-${var.aws_region}c"] # insert values here
  }
}

locals {
  subnet_arns = [for d in data.aws_subnet_ids.selected.ids : "arn:aws:ec2:${var.aws_region}:${var.aws_account_id_nonprod}:subnet/${d}"]
  #ids = [for d in var.data: d["id"]]  #same
}

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}
