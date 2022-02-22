data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.vpc_terraform_state_key
    region = var.aws_region
  }
}

data "aws_db_instance" "dos_db" {
  db_instance_identifier = var.dos_db_name
}

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}
