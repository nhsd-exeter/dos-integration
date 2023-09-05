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

resource "aws_security_group_rule" "database_writer_allow_in_from_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  security_group_id        = data.aws_security_group.db_writer_sg.id
  description              = "Allow access in from DI lambdas to DoS Aurora Postgres Writer DB - ${var.environment}"
}

resource "aws_security_group_rule" "database_reader_allow_in_from_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  security_group_id        = data.aws_security_group.db_reader_sg.id
  description              = "Allow access in from DI lambdas to DoS Aurora Postgres Reader DB - ${var.environment}"
}
