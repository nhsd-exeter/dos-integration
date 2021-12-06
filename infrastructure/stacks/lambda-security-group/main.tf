resource "aws_security_group" "uec_dos_int_lambda_sg" {
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  name        = var.lambda_security_group_name
  description = "DI Lambda Security Group"

  tags = {
    Name = var.lambda_security_group_name
  }

}

resource "aws_security_group_rule" "allow_all_out" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
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
