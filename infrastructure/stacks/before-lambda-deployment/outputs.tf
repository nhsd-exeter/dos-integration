output "kms_key_id" {
  description = "The KMS key arn we just created"
  value       = data.aws_kms_key.signing_key.arn
}
