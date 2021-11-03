resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "codepipeline_policy"
  role = aws_iam_role.codepipeline_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:PutObjectAcl",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::${var.source_bucket}",
        "arn:aws:s3:::${var.source_bucket}/*",
        "${module.codepipeline_artefact_bucket.s3_bucket_arn}",
        "${module.codepipeline_artefact_bucket.s3_bucket_arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
      "Resource": "arn:aws:codebuild:${var.aws_region}:${var.aws_account_id_nonprod}:project/uec-pu-*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "codebuild_policy" {
  role = aws_iam_role.codebuild_role.name

  policy = <<EOF
{
	"Version": "2012-10-17",
	"Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id_nonprod}:table/${var.texas_terraform_state_lock}"
    },
    {
      "Effect": "Allow",
      "Action": "lambda:*",
      "Resource": [
        "arn:aws:lambda:${var.aws_region}:${var.aws_account_id_nonprod}:function:uec-pu-*",
        "arn:aws:lambda:${var.aws_region}:${var.aws_account_id_nonprod}:layer:uec-pu-*",
        "arn:aws:lambda:${var.aws_region}:${var.aws_account_id_nonprod}:event-source-mapping:uec-pu-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "events:*",
      "Resource": [
        "arn:aws:events:${var.aws_region}:${var.aws_account_id_nonprod}:uec-pu-*",
        "arn:aws:events:${var.aws_region}:${var.aws_account_id_nonprod}:rule/uec-pu-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:DescribeImageScanFindings",
        "ecr:GetLifecyclePolicyPreview",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:DescribeImages",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetRepositoryPolicy",
        "ecr:GetLifecyclePolicy",
        "ecr:GetRegistryPolicy",
        "ecr:DescribeRegistry"
      ],
      "Resource": "arn:aws:ecr:${var.aws_region}:${var.aws_account_id_mgmt}:repository/uec-pu*"
    },
    {
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:*"
      ],
      "Resource": "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id_nonprod}:secret:uec-pu-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:CreateReportGroup",
        "codebuild:CreateReport",
        "codebuild:BatchPutTestCases",
        "codebuild:BatchPutCodeCoverages",
        "codebuild:UpdateReport"
      ],
      "Resource": [
        "arn:aws:codebuild:${var.aws_region}:${var.aws_account_id_nonprod}:project/uec-pu-*",
        "arn:aws:codebuild:${var.aws_region}:${var.aws_account_id_nonprod}:report-group/uec-pu-*"
        ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:*"
        ],
      "Resource": [
        "arn:aws:iam::${var.aws_account_id_nonprod}:role/uec-pu-*",
        "arn:aws:iam::${var.aws_account_id_nonprod}:role/UECPU*"
        ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeSecurityGroups",
        "logs:*",
        "s3:*"
        ],
      "Resource": "*"
    }
  ]
}
EOF
}
