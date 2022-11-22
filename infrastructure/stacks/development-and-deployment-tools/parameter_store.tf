resource "aws_ssm_parameter" "blue_green_deployment_new_version" {
  #checkov:skip=CKV2_AWS_34:Value does not contain sensitive data so it is ok to be stored in plain text
  name           = var.blue_green_deployment_new_version_parameter_name
  description    = "The new version of the application to be deployed to the blue environment"
  type           = "String"
  insecure_value = "NA"
  lifecycle {
    ignore_changes = [insecure_value]
  }
  # insecure_value is updated by the blue-green deployment pipeline process
  # and should not be updated by Terraform unless necessary
}
