resource "aws_security_group" "uec_dos_int_lambda_sg" {
  #checkov:skip=CKV2_AWS_5:Attached outside of Terraform
  vpc_id      = data.aws_vpc.texas_vpc.id
  name        = var.lambda_security_group_name
  description = "DI Lambda Security Group"

  tags = {
    Name = var.lambda_security_group_name
  }
}

#tfsec:ignore:aws-vpc-no-public-egress-sgr
resource "aws_security_group_rule" "allow_https_out" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  description       = "Allow all HTTPS outbound traffic"
}

#tfsec:ignore:aws-vpc-no-public-egress-sgr
resource "aws_security_group_rule" "allow_postgres_out" {
  type              = "egress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  description       = "Allow all Postgres outbound traffic"
}
resource "aws_security_group_rule" "database_allow_in_from_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  security_group_id        = data.aws_security_group.dos_db_sg.id
  description              = "Allow access in from UEC DI lambda to DoS Postgres DB - ${var.environment}}"
}

resource "aws_security_group_rule" "database_replica_allow_in_from_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  security_group_id        = data.aws_security_group.dos_db_replica_sg.id
  description              = "Allow access in from UEC DI lambda to DoS Replica Postgres DB"
}
