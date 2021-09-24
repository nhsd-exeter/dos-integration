module "autoscaling" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "3.8.0"
  tags    = var.context.tags

  name = var.name

  lc_name  = var.lc_name
  asg_name = var.asg_name

  health_check_type         = var.health_check_type
  min_size                  = var.min_size
  max_size                  = var.max_size
  desired_capacity          = var.desired_capacity
  wait_for_capacity_timeout = var.wait_for_capacity_timeout

  # TODO: Expose all the settings as variables
}
