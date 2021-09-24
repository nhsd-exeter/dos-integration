module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "2.5.0"
  tags    = var.context.tags

  name               = var.name
  container_insights = true
  capacity_providers = ["FARGATE"]
  default_capacity_provider_strategy = {
    capacity_provider = "FARGATE"
  }
}
