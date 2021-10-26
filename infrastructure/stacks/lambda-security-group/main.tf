resource "aws_security_group" "uec_dos_int_lambda_sg" {
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  name        = var.lambda_security_group_name
  description = "DI Lambda Security Group"

  tags = merge(
    local.standard_tags,
    {
      "Name" = var.lambda_security_group_name
    },
  )
}

resource "aws_security_group_rule" "allow_all_out" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.uec_dos_int_lambda_sg.id
}
