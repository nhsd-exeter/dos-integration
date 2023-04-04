# ##############
# # Codebuild buildspecs
# ##############
data "template_file" "unit_tests_buildspec" {
  template = file("buildspecs/unit-tests-buildspec.yml")
}

data "template_file" "build_buildspec" {
  template = file("buildspecs/build-buildspec.yml")
}

data "template_file" "build_arm_buildspec" {
  template = file("buildspecs/build-arm-buildspec.yml")
}

data "template_file" "build_image_buildspec" {
  template = file("buildspecs/build-image-buildspec.yml")
}

data "template_file" "deploy_full_environment_buildspec" {
  template = file("buildspecs/deploy-full-environment-buildspec.yml")
}

data "template_file" "integration_tests_buildspec" {
  template = file("buildspecs/integration-tests-buildspec.yml")
}

data "template_file" "setup_dos_environment_buildspec" {
  template = file("buildspecs/setup-dos-environment-buildspec.yml")
}

data "template_file" "delete_nonprod_environment_from_tag_buildspec" {
  template = file("buildspecs/delete-nonprod-environment-from-tag-buildspec.yml")
}

data "template_file" "delete_nonprod_environment_on_pr_merged_buildspec" {
  template = file("buildspecs/delete-nonprod-environment-on-pr-merged-buildspec.yml")
}

data "template_file" "build_environment_buildspec" {
  template = file("buildspecs/build-environment-buildspec.yml")
}

data "template_file" "delete_ecr_images_buildspec" {
  template = file("buildspecs/delete-ecr-images-buildspec.yml")
}

data "template_file" "build_release_buildspec" {
  template = file("buildspecs/build-release-buildspec.yml")
}

data "template_file" "delete_release_environment_and_pipeline_on_pr_merged_buildspec" {
  template = file("buildspecs/delete-release-environment-and-pipeline-on-pr-merged-buildspec.yml")
}

data "template_file" "tag_release_images_on_branch_delete_buildspec" {
  template = file("buildspecs/tag-release-images-on-branch-delete-buildspec.yml")
}

data "template_file" "build_cicd_blue_green_deployment_artefact_buildspec" {
  template = file("buildspecs/build-cicd-blue-green-deployment-artefact-buildspec.yml")
}

data "template_file" "deploy_blue_green_environment_buildspec" {
  template = file("buildspecs/deploy-blue-green-environment-buildspec.yml")
}

data "template_file" "deploy_shared_resources_environment_buildspec" {
  template = file("buildspecs/deploy-shared-resources-environment-buildspec.yml")
}

data "template_file" "delete_blue_green_environment_buildspec" {
  template = file("buildspecs/delete-blue-green-environment-buildspec.yml")
}

data "template_file" "build_cicd_shared_resources_artefact_buildspec" {
  template = file("buildspecs/build-cicd-shared-resources-artefact-buildspec.yml")
}

data "template_file" "rollback_blue_green_deployment_buildspec" {
  template = file("buildspecs/rollback-blue-green-deployment-buildspec.yml")
}

# ##############
# # IAM
# ##############

data "aws_iam_policy_document" "kms_policy" {
  #checkov:skip=CKV_AWS_109
  #checkov:skip=CKV_AWS_111
  policy_id     = null
  source_json   = null
  override_json = null
  version       = "2012-10-17"
  statement {
    sid    = null
    effect = "Allow"
    principals {
      identifiers = [
        "arn:aws:iam::${var.aws_account_id}:root",
        "arn:aws:iam::${var.aws_account_id}:role/${var.developer_role_name}"
      ]
      type = "AWS"
    }
    actions = [
      "kms:*"
    ]
    not_actions = []
    resources = [
      "*"
    ]
    not_resources = []
  }
  statement {
    sid    = null
    effect = "Allow"
    principals {
      identifiers = [
        "cloudwatch.amazonaws.com"
      ]
      type = "Service"
    }
    actions = [
      "kms:*"
    ]
    not_actions = []
    resources = [
      "*"
    ]
    not_resources = []
  }
}

data "aws_iam_role" "pipeline_role" {
  name = "UECDoSINTPipelineRole"
}

# ##############
# # VPC
# ##############

data "aws_vpc" "texas_mgmt_vpc" {
  tags = {
    "Name" = var.mgmt_vpc_name
  }
}
data "aws_subnet" "vpc_subnet_one" {
  filter {
    name   = "tag:Name"
    values = ["${var.mgmt_vpc_name}-private-${var.aws_region}a"]
  }
}

data "aws_subnet" "vpc_subnet_two" {
  filter {
    name   = "tag:Name"
    values = ["${var.mgmt_vpc_name}-private-${var.aws_region}b"]
  }
}

data "aws_subnet" "vpc_subnet_three" {
  filter {
    name   = "tag:Name"
    values = ["${var.mgmt_vpc_name}-private-${var.aws_region}c"]
  }
}
