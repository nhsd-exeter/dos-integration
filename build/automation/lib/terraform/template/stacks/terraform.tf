# ==============================================================================
# Terraform

terraform {
  required_version = ">= 0.13.5"
  backend "s3" { encrypt = true } # Please, do not change this line!
}
