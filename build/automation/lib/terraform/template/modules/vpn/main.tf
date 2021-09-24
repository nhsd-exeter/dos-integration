module "vpn" {
  source  = "../autoscaling"
  context = var.context

  name = var.name

  lc_name  = "${var.name}-lc"
  asg_name = "${var.name}-asg"

  health_check_type         = "EC2"
  min_size                  = 0
  max_size                  = 1
  desired_capacity          = 1
  wait_for_capacity_timeout = 0

  # TODO: Follow the example https://github.com/terraform-aws-modules/terraform-aws-autoscaling

  create_lc  = false
  create_asg = false
}
