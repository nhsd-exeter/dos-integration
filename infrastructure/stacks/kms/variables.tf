##############################
# KMS
##############################

variable "ddb_kms_key_alias" {
  description = "Key alias for the ddb kms key"
}

variable "sqs_kms_key_alias" {
  description = "Key alias for the sqs kms key"
}
