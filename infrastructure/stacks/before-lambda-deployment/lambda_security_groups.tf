resource "aws_security_group" "uec_dos_int_lambda_sg" {
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  name        = var.lambda_security_group_name
  description = "DI Lambda Security Group"

  tags = {
    Name = var.lambda_security_group_name
  }
}

resource "aws_security_group_rule" "allow_https_out" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  description       = "Allow all HTTPS outbound traffic"
}

resource "aws_security_group_rule" "allow_postgres_out" {
  type              = "egress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  description       = "Allow all Postgres outbound traffic"
}
resource "aws_security_group_rule" "allow_in_from_lambda" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
  security_group_id        = data.aws_db_instance.dos_db.vpc_security_groups[0]
  description              = "Allow access in from UEC DI lambda to Postgres DB"
}
