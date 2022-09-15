output "s3_bucket_id" {
  description = "The S3 bucket ID we just created"
  value       = module.s3_bucket.s3_bucket_id
}

output "s3_bucket_arn" {
  description = "The S3 bucket ARN we just created"
  value       = module.s3_bucket.s3_bucket_arn
}
