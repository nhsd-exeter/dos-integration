module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "5.10.0"
  tags    = var.context.tags

  name                        = var.name
  load_balancer_type          = "application"
  listener_ssl_policy_default = "ELBSecurityPolicy-TLS-1-2-2017-01"

  vpc_id          = var.vpc_id
  subnets         = var.subnets
  security_groups = concat([module.alb-security-group.this_security_group_id], var.security_groups)

  http_tcp_listeners = [
    {
      port        = 80
      protocol    = "HTTP"
      action_type = "redirect"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  ]
  https_listeners = [
    {
      port               = 443
      protocol           = "HTTPS"
      certificate_arn    = var.certificate_arn
      target_group_index = 0
    }
  ]
  https_listener_rules = [
    {
      https_listener_index = 0
      priority             = 100
      actions = [{
        type         = "fixed-response"
        content_type = "text/plain"
        message_body = "OK"
        status_code  = "200"
      }]
      conditions = [{
        path_patterns = ["/*"]
      }]
    }
  ]
  target_groups = [
    {
      name             = "${var.name}-tg"
      backend_protocol = "HTTPS"
      backend_port     = 443
      target_type      = "ip"
    }
  ]
  target_group_tags = var.context.tags
}

module "alb-security-group" {
  source  = "../security-group"
  context = var.context

  name        = "${var.name}-sg"
  description = "Default ALB Security Group"
  vpc_id      = var.vpc_id

  ingress_rules       = ["http-80-tcp", "https-443-tcp"]
  ingress_cidr_blocks = ["0.0.0.0/0"]
}
