locals {
  include_policies = length(var.principals_full_access) + length(var.principals_readonly_access) + length(var.principals_dont_deny_delete) > 0 ? true : false
}

resource "aws_ecr_repository" "repository" {
  for_each = toset(var.names)
  name     = each.key

  image_tag_mutability = var.image_tag_mutability
  dynamic "encryption_configuration" {
    for_each = var.encryption_configuration == null ? [] : [var.encryption_configuration]
    content {
      encryption_type = encryption_configuration.value.encryption_type
      kms_key         = encryption_configuration.value.kms_key
    }
  }
  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  tags = var.context.tags
}

resource "aws_ecr_lifecycle_policy" "lifecycle-policy" {
  for_each   = toset(var.names)
  repository = aws_ecr_repository.repository[each.value].name

  policy = jsonencode({
    rules = concat(local.protected_tag_rules, local.untagged_image_rule, local.remove_old_image_rule)
  })
}

locals {
  protected_tag_rules = [
    for index, tagPrefix in zipmap(range(length(var.protected_tags)), tolist(var.protected_tags)) :
    {
      rulePriority = tonumber(index) + 1
      description  = "Protects images tagged with ${tagPrefix}"
      selection = {
        tagStatus     = "tagged"
        tagPrefixList = [tagPrefix]
        countType     = "imageCountMoreThan"
        countNumber   = 999999
      }
      action = {
        type = "expire"
      }
    }
  ]
  untagged_image_rule = [{
    rulePriority = length(var.protected_tags) + 1
    description  = "Remove untagged images"
    selection = {
      tagStatus   = "untagged"
      countType   = "imageCountMoreThan"
      countNumber = 1
    }
    action = {
      type = "expire"
    }
  }]
  remove_old_image_rule = [{
    rulePriority = length(var.protected_tags) + 2
    description  = "Rotate images when reach ${var.max_image_count} images stored",
    selection = {
      tagStatus   = "any"
      countType   = "imageCountMoreThan"
      countNumber = var.max_image_count
    }
    action = {
      type = "expire"
    }
  }]
}

data "aws_iam_policy_document" "repository-readonly-access-policy-document" {
  count = length(var.principals_readonly_access) > 0 ? 1 : 0

  statement {
    sid    = "ReadOnlyAccess"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = var.principals_readonly_access
    }
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:DescribeImages",
      "ecr:DescribeImageScanFindings",
      "ecr:DescribeRepositories",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetLifecyclePolicy",
      "ecr:GetLifecyclePolicyPreview",
      "ecr:GetRepositoryPolicy",
      "ecr:ListImages",
      "ecr:ListTagsForResource",
    ]
  }
}

data "aws_iam_policy_document" "repository-full-access-policy-document" {
  count = length(var.principals_full_access) > 0 ? 1 : 0

  statement {
    sid    = "FullAccess"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = var.principals_full_access
    }
    actions = [
      "ecr:*",
    ]
  }
}

data "aws_iam_policy_document" "repository-deny-delete-policy-document" {
  count = length(var.principals_dont_deny_delete) > 0 ? 1 : 0

  statement {
    sid    = "DenyDelete"
    effect = "Deny"
    not_principals {
      type        = "AWS"
      identifiers = var.principals_dont_deny_delete
    }
    actions = [
      "ecr:BatchDeleteImage",
      "ecr:DeleteRepository",
    ]
  }
}

data "aws_iam_policy_document" "empty" {
  count = local.include_policies ? 1 : 0
}

data "aws_iam_policy_document" "repository-policy-document" {
  count = local.include_policies ? 1 : 0

  # TODO: There must be a simpler way to combine policies, also include `repository-deny-delete-policy-document`
  source_json   = length(var.principals_readonly_access) > 0 ? join("", [data.aws_iam_policy_document.repository-readonly-access-policy-document[0].json]) : join("", [data.aws_iam_policy_document.empty[0].json])
  override_json = length(var.principals_full_access) > 0 ? join("", [data.aws_iam_policy_document.repository-full-access-policy-document[0].json]) : join("", [data.aws_iam_policy_document.empty[0].json])
}

resource "aws_ecr_repository_policy" "repository-policy" {
  for_each   = toset(local.include_policies ? var.names : [])
  repository = aws_ecr_repository.repository[each.value].name
  policy     = join("", data.aws_iam_policy_document.repository-policy-document.*.json)
}
