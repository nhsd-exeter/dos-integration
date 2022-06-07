terraform {
  backend "s3" {
    encrypt = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.17.1"
    }
    template = {
      source  = "hashicorp/random"
      version = "~> 3.2.0"
    }
  }
}
