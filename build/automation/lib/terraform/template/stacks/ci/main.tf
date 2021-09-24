module "NAME_TEMPLATE_TO_REPLACE-ecr" {
  source  = "../../modules/ecr"
  context = local.context

  names          = ["ns/test1", "ns/test2"]
  protected_tags = ["live-", "demo-"]

  # TODO: Move configuration to the Make DevOps automation scripts
}
