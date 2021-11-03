##########################
# INFRASTRUCTURE COMPONENT
##########################

############
# AWS COMMON
############

variable "aws_profile" {
  description = "The AWS profile"
}

variable "aws_region" {
  description = "The AWS region"
}

variable "aws_account_id" {
  description = "AWS account Number for Athena log location"
}

variable "aws_account_id_nonprod" {
  description = ""
}
variable "aws_account_id_mgmt" {
  description = ""
}
variable "aws_account_id_prod" {
  description = ""
}

variable "aws_account_id_identities" {
  description = ""
}

variable "aws_account_id_tools" {
  description = ""
  default     = "00000000000"
}
variable "aws_account_id_live_parent" {
  description = ""
}
# ##############
# # TEXAS COMMON
# ##############

variable "profile" {
  description = "The tag used to identify profile e.g. dev, test, live, ..."
}

variable "service_name" {
  description = "The tag used to identify the service the resource belongs to"
  default     = "uec-pu"
}

variable "texas_s3_logs_bucket" {
  description = "The texas s3 log bucket for s3 bucket logs"
}

variable "texas_terraform_state_store" {
  description = ""
}

variable "texas_terraform_state_lock" {
  description = ""
}
# ##############
# # CodePipeline
# ##############

variable "development_pipeline_name" {
  description = ""
}

variable "di_test_image" {
  description = ""
}

variable "build_image" {
  description = ""
}

variable "codepipeline_role" {
  description = ""
}

# ##############
# # CodePipeline Arefact Bucket
# ##############

variable "codepipeline_artefact_bucket_name" {
  description = "The s3 artefact bucket for output artefacts"
}

# ##############
# # CodeBuild
# ##############

variable "unit_test_codebuild_project_name" {
  description = "Name of the unit test codebuild project"
}

variable "build_and_deploy_codebuild_project_name" {
  description = "Name of the build and deploy codebuild project"
}

variable "e2e_test_codebuild_project_name" {
  description = "Name of the E2E test codebuild project"
}

variable "codebuild_role" {
  description = ""
}

variable "source_bucket" {
  description = ""
}

# ##############
# # Environment Variables
# ##############
