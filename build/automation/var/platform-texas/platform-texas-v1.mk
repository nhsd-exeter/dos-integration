TEXAS_VERSION = v1

AWS_ECR = $(or $(AWS_ACCOUNT_ID_MGMT), 000000000000).dkr.ecr.$(AWS_DEFAULT_REGION).amazonaws.com
AWS_REGION = eu-west-2
AWS_DEFAULT_REGION = $(AWS_REGION)
AWS_ALTERNATIVE_REGION = eu-west-1
AWS_ROLE_PIPELINE = jenkins_assume_role
AWS_ROLE_SESSION = jenkins
AWS_ROLE = $(if $(HUDSON_URL),$(AWS_ROLE_PIPELINE),Developer)
AWS_ALB_SSL_TLS_POLICY = ELBSecurityPolicy-TLS-1-2-2017-01

# ==============================================================================

TEXAS_HOSTED_ZONE = k8s-$(AWS_ACCOUNT_NAME).texasplatform.uk
TEXAS_HOSTED_ZONE_NONPROD = k8s-nonprod.texasplatform.uk
TEXAS_HOSTED_ZONE_PROD = k8s-prod.texasplatform.uk
TEXAS_K8S_KUBECONFIG_FILE = nhsd-texasplatform-kubeconfig-lk8s-$(AWS_ACCOUNT_NAME)/live-leks-cluster_kubeconfig
TEXAS_S3_LOGS_BUCKET = nhsd-texasplatform-s3-logs-lk8s-$(AWS_ACCOUNT_NAME)
TEXAS_TERRAFORM_STATE_LOCK = nhsd-texasplatform-terraform-service-state-lock-texas-lk8s-$(AWS_ACCOUNT_NAME)
TEXAS_TERRAFORM_STATE_STORE = nhsd-texasplatform-terraform-service-state-store-lk8s-$(AWS_ACCOUNT_NAME)

# ==============================================================================

TF_VAR_aws_profile = nhsd-ddc-exeter-texas-live-lk8s-$(AWS_ACCOUNT_NAME)
TF_VAR_platform_zone = $(TEXAS_HOSTED_ZONE)

TF_VAR_eks_terraform_state_key = eks/terraform.tfstate
TF_VAR_route53_terraform_state_key = route53/terraform.tfstate
TF_VAR_security_groups_k8s_terraform_state_key = security-groups-k8s/terraform.tfstate
TF_VAR_security_groups_terraform_state_key = security-groups/terraform.tfstate
TF_VAR_vpc_terraform_state_key = vpc/terraform.tfstate
