resource "aws_security_group" "codebuild_sg" {
  vpc_id      = data.aws_vpc.texas_mgmt_vpc.id
  name        = "${var.project_id}-${var.environment}-codebuild-sg"
  description = "Codebuild security group for accessing Jenkins"
}

#tfsec:ignore:aws-vpc-no-public-egress-sgr
resource "aws_security_group_rule" "allow_https_out" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.codebuild_sg.id
  description       = "Lets out HTTPS traffic to access Jenkins"
}
