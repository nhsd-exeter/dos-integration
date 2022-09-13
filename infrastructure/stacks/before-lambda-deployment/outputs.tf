output "kms_key_id" {
  description = "The KMS key ID we just created"
  value       = aws_kms_key.signing_key.id
}
