output "s3_bucket_id" {
  description = "The S3 bucket ID we just created"
  value       = "s3_bucket.${var.name}.id"
}

output "s3_bucket_arn" {
  description = "The S3 bucket ARN we just created"
  value       = "arn:aws:s3:::${var.name}"
}
