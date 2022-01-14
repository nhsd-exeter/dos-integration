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
        "${module.codepipeline_artefact_bucket.s3_bucket_arn}",
        "${module.codepipeline_artefact_bucket.s3_bucket_arn}/*"
      ]
    },
    {
      "Action": [
          "codestar-connections:UseConnection"
      ],
      "Resource": "arn:aws:codestar-connections:${var.aws_region}:${var.aws_account_id_nonprod}:connection/*",
      "Effect": "Allow"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
      "Resource": "arn:aws:codebuild:${var.aws_region}:${var.aws_account_id_nonprod}:project/uec-dos-int-*"
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
          "s3:Put*",
          "s3:List*",
          "s3:Get*"
      ],
      "Resource": [
          "arn:aws:s3:::nhsd-texasplatform-terraform-service-state-store-lk8s-nonprod/*",
          "arn:aws:s3:::nhsd-texasplatform-terraform-service-state-store-lk8s-nonprod*"
      ]
    },
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
      "Action": "dynamodb:*",
      "Resource": "arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id_nonprod}:table/uec-dos-int*"
    },
    {
      "Effect": "Allow",
      "Action": "lambda:*",
      "Resource": [
        "arn:aws:lambda:${var.aws_region}:${var.aws_account_id_nonprod}:function:uec-dos-int*",
        "arn:aws:lambda:${var.aws_region}:${var.aws_account_id_nonprod}:layer:uec-dos-int*",
        "arn:aws:logs:${var.aws_region}:${var.aws_account_id_nonprod}:log-group:/aws/lambda/uec-dos-int*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:GetEventSourceMapping",
        "lambda:CreateEventSourceMapping",
        "lambda:DeleteEventSourceMapping",
        "lambda:UpdateEventSourceMapping"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "events:*",
      "Resource": [
        "arn:aws:events:${var.aws_region}:${var.aws_account_id_nonprod}:uec-dos-int*",
        "arn:aws:events:${var.aws_region}:${var.aws_account_id_nonprod}:*/uec-dos-int*"
      ]
    },

    {
        "Effect": "Allow",
        "Action": "kinesis:*",
        "Resource": "arn:aws:kinesis:${var.aws_region}:${var.aws_account_id_nonprod}:*uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "logs:*",
        "Resource": "arn:aws:logs:${var.aws_region}:${var.aws_account_id_nonprod}:log-group:uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "logs:*",
        "Resource": "arn:aws:logs:${var.aws_region}:${var.aws_account_id_nonprod}:log-group:*uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "logs:*",
        "Resource": "arn:aws:logs:${var.aws_region}:${var.aws_account_id_nonprod}:log-group:*:log-stream:uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "logs:*",
        "Resource": "arn:aws:logs:${var.aws_region}:${var.aws_account_id_nonprod}:log-group:*:log-stream:*uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "sqs:*",
        "Resource": "arn:aws:sqs:${var.aws_region}:${var.aws_account_id_nonprod}:uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "cloudwatch:*",
        "Resource": "arn:aws:cloudwatch:${var.aws_region}:${var.aws_account_id_nonprod}:alarm:uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "cloudwatch:*",
        "Resource": "arn:aws:cloudwatch::${var.aws_account_id_nonprod}${var.aws_account_id_nonprod}:*uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "SNS:*",
        "Resource": "arn:aws:sns:${var.aws_region}:${var.aws_account_id_nonprod}:uec-dos-int*"
    },
    {
        "Effect": "Allow",
        "Action": "resource-groups:*",
        "Resource": "arn:aws:resource-groups:${var.aws_region}:${var.aws_account_id_nonprod}:group/uec-dos-int*"
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
        "ecr:DescribeRegistry",
        "ecr:InitiateLayerUpload",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ],
      "Resource": [
        "arn:aws:ecr:${var.aws_region}:${var.aws_account_id_mgmt}:repository/uec-dos/int*",
        "arn:aws:ecr:${var.aws_region}:${var.aws_account_id_nonprod}:repository/uec-dos/int*"
      ]
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
      "Resource": [
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id_nonprod}:secret:uec-dos-int-*",
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id_nonprod}:secret:core-dos-dev/deployment*",
        "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id_nonprod}:secret:uec-pu-updater/deployment*"
      ]
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
        "arn:aws:codebuild:${var.aws_region}:${var.aws_account_id_nonprod}:project/uec-dos-int-*",
        "arn:aws:codebuild:${var.aws_region}:${var.aws_account_id_nonprod}:report-group/uec-dos-int-*"
        ]
    },
    {
      "Sid": "Firehose",
      "Effect": "Allow",
      "Action": [
          "firehose:DescribeDeliveryStream"
      ],
      "Resource": [
        "arn:aws:firehose:${var.aws_region}:${var.aws_account_id_nonprod}:deliverystream/uec-dos-int-*"
      ]
    },
    {
      "Sid": "iam",
      "Effect": "Allow",
      "Action": [
          "iam:PassRole",
          "iam:CreateRole",
          "iam:GetRole",
          "iam:DeleteRole",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy"
      ],
      "Resource": [
          "arn:aws:iam::${var.aws_account_id_nonprod}:role/service-role/UECDoSINT*",
          "arn:aws:iam::${var.aws_account_id_nonprod}:role/service-role/UECDosInt*",
          "arn:aws:iam::${var.aws_account_id_nonprod}:role/uec-dos-int*",
          "arn:aws:iam::${var.aws_account_id_nonprod}:role/service-role/UECPU*"
      ]
    },
    {
      "Sid": "apiGateway",
      "Effect": "Allow",
      "Action": [
        "apigateway:*"
      ],
      "Resource": "*"
  },
  {
      "Sid": "acmList",
      "Effect": "Allow",
      "Action": [
          "acm:GetAccountConfiguration",
          "acm:ListCertificates"
      ],
      "Resource": "*"
  },
  {
      "Effect": "Allow",
      "Action": "rds:*",
      "Resource": [
          "arn:aws:rds:${var.aws_region}:${var.aws_account_id_nonprod}:*:uec-pu*",
          "arn:aws:rds:${var.aws_region}:${var.aws_account_id_nonprod}:*:uec-dos*"
      ]
  },
  {
    "Effect": "Allow",
    "Action": [
      "rds:DescribeDBInstances",
      "rds:ListTagsForResource"
    ],
    "Resource": [
      "arn:aws:rds:${var.aws_region}:${var.aws_account_id_nonprod}:db:*"
    ]
  },
  {
      "Sid": "acmRead",
      "Effect": "Allow",
      "Action": [
          "acm:ExportCertificate",
          "acm:DescribeCertificate",
          "acm:GetCertificate",
          "apigateway:POST",
          "acm:ListTagsForCertificate"
      ],
      "Resource": [
          "arn:aws:apigateway:${var.aws_region}::/apikeys",
          "arn:aws:apigateway:${var.aws_region}::/restapis/*uec-dos-int*/authorizers",
          "arn:aws:apigateway:${var.aws_region}::/restapis",
          "arn:aws:apigateway:${var.aws_region}::/restapis/*uec-dos-int*/stages",
          "arn:aws:apigateway:${var.aws_region}::/vpclinks",
          "arn:aws:apigateway:${var.aws_region}::/usageplans",
          "arn:aws:apigateway:${var.aws_region}::/usageplans/*uec-dos-int*/keys",
          "arn:aws:acm:${var.aws_region}:${var.aws_account_id_nonprod}:certificate/*"
      ]
    },
    {
      "Sid": "r53",
      "Effect": "Allow",
      "Action": [
        "route53resolver:List*",
        "route53resolver:Get*",
        "route53domains:List*",
        "route53domains:Get*",
        "route53:TestDNSAnswer",
        "route53:List*",
        "route53:Get*",
        "route53:Describe*",
        "route53:ChangeResourceRecordSets"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ssmget",
      "Effect": "Allow",
      "Action": [
          "ssm:GetParameterHistory",
          "ssm:GetParametersByPath",
          "ssm:GetPatchBaselineForPatchGroup",
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:GetPatchBaseline"
      ],
      "Resource": [
          "arn:aws:ssm:${var.aws_region}:${var.aws_account_id_nonprod}:patchbaseline/*uec-dos-int*",
          "arn:aws:ssm:${var.aws_region}:${var.aws_account_id_nonprod}:parameter/*uec-dos-int*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:*"
        ],
      "Resource": [
        "arn:aws:iam::${var.aws_account_id_nonprod}:role/uec-dos-int*",
        "arn:aws:iam::${var.aws_account_id_nonprod}:role/UECPU*"
        ]
    },
    {
      "Sid": "CFGeneral",
      "Effect": "Allow",
      "Action": [
          "cloudformation:ListStacks",
          "cloudformation:ListStackSetOperationResults",
          "cloudformation:ListStackSets",
          "cloudformation:ListStackSetOperations",
          "cloudformation:ListStackInstances",
          "cloudformation:ListChangeSets",
          "cloudformation:DescribeStacks",
          "cloudformation:ListStackResources",
          "cloudformation:ValidateTemplate"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CFDoSInt",
      "Effect": "Allow",
      "Action": [
          "cloudformation:CreateUploadBucket",
          "cloudformation:RegisterType",
          "cloudformation:DescribeStackDriftDetectionStatus",
          "cloudformation:ListExports",
          "cloudformation:SetTypeDefaultVersion",
          "cloudformation:ActivateType",
          "cloudformation:RegisterPublisher",
          "cloudformation:ListTypes",
          "cloudformation:DeactivateType",
          "cloudformation:SetTypeConfiguration",
          "cloudformation:DeregisterType",
          "cloudformation:ListTypeRegistrations",
          "cloudformation:EstimateTemplateCost",
          "cloudformation:BatchDescribeTypeConfigurations",
          "cloudformation:DescribeAccountLimits",
          "cloudformation:CreateStackSet",
          "cloudformation:DescribeType",
          "cloudformation:ListImports",
          "cloudformation:PublishType",
          "cloudformation:DescribePublisher",
          "cloudformation:DescribeTypeRegistration",
          "cloudformation:TestType",
          "cloudformation:ValidateTemplate",
          "cloudformation:ListTypeVersions",
          "cloudformation:DetectStackSetDrift",
          "cloudformation:ImportStacksToStackSet",
          "cloudformation:DeleteStackInstances",
          "cloudformation:DetectStackDrift",
          "cloudformation:CancelUpdateStack",
          "cloudformation:UpdateStackInstances",
          "cloudformation:UpdateTerminationProtection",
          "cloudformation:RecordHandlerProgress",
          "cloudformation:DescribeStackResource",
          "cloudformation:UpdateStackSet",
          "cloudformation:CreateChangeSet",
          "cloudformation:CreateStackInstances",
          "cloudformation:DeleteChangeSet",
          "cloudformation:ContinueUpdateRollback",
          "cloudformation:DetectStackResourceDrift",
          "cloudformation:DescribeStackEvents",
          "cloudformation:DescribeStackSetOperation",
          "cloudformation:UpdateStack",
          "cloudformation:StopStackSetOperation",
          "cloudformation:DescribeChangeSet",
          "cloudformation:ExecuteChangeSet",
          "cloudformation:SetStackPolicy",
          "cloudformation:DescribeStackInstance",
          "cloudformation:DescribeStackResources",
          "cloudformation:SignalResource",
          "cloudformation:DeleteStackSet",
          "cloudformation:GetTemplateSummary",
          "cloudformation:DescribeStackResourceDrifts",
          "cloudformation:GetStackPolicy",
          "cloudformation:DescribeStackSet",
          "cloudformation:CreateStack",
          "cloudformation:GetTemplate",
          "cloudformation:DeleteStack",
          "cloudformation:TagResource",
          "cloudformation:UntagResource"
      ],
      "Resource": [
          "arn:aws:cloudformation:${var.aws_region}:${var.aws_account_id_nonprod}:stackset/uec-dos-int*:*",
          "arn:aws:cloudformation:${var.aws_region}:${var.aws_account_id_nonprod}:stackset-target/uec-dos-int*",
          "arn:aws:cloudformation:${var.aws_region}:${var.aws_account_id_nonprod}:stack/uec-dos-int*/*",
          "arn:aws:cloudformation:${var.aws_region}:${var.aws_account_id_nonprod}:type/resource/uec-dos-int*"
      ]
    },
    {
        "Effect": "Allow",
        "Action": "ec2:*",
        "Resource": "*",
        "Condition": {
            "StringEquals": {
                "ec2:ResourceTag/Service": "uec-dos-int"
            }
        }
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:Create*",
        "ec2:AuthorizeSecurityGroupIngress",
        "logs:*",
        "s3:*"
        ],
      "Resource": "*"
    }
  ]
}
EOF
}
