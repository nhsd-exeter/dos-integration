resource "aws_ssm_parameter" "pharmacy_first_phase_one_parameter" {
  #checkov:skip=CKV2_AWS_34:Value does not contain sensitive data so it is ok to be stored in plain text
  name        = var.pharmacy_first_phase_one_parameter_name
  description = "The feature flag for pharamcy first phase one"
  type        = "String"
  value       = "True"

}
