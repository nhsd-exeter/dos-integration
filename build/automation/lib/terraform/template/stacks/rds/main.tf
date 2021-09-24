module "NAME_TEMPLATE_TO_REPLACE-rds" {
  source  = "../../modules/rds"
  context = local.context

  db_instance = var.db_instance
  db_port     = var.db_port
  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password

  vpc_id             = data.terraform_remote_state.networking.outputs.vpc_id
  subnet_ids         = data.terraform_remote_state.networking.outputs.vpc_intra_subnets
  security_group_ids = [data.terraform_remote_state.networking.outputs.default_security_group_id]

  # # This code block is for the Texas v1
  # vpc_id             = data.terraform_remote_state.vpc.outputs.vpc_id
  # subnet_ids         = data.terraform_remote_state.vpc.outputs.private_subnets
  # security_group_ids = [data.terraform_remote_state.security_groups_k8s.outputs.eks_worker_additional_sg_id]
}
