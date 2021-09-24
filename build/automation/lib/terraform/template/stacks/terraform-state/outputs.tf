# ==============================================================================
# Outputs

# --------------------------------------
# s3

output "s3_bucket_id" {
  description = "The name of the bucket."
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_id
}
output "s3_bucket_arn" {
  description = "The ARN of the bucket. Will be of format arn:aws:s3:::bucketname."
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_arn
}
output "s3_bucket_bucket_domain_name" {
  description = "The bucket domain name. Will be of format bucketname.s3.amazonaws.com."
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_bucket_domain_name
}
output "s3_bucket_bucket_regional_domain_name" {
  description = "The bucket region-specific domain name. The bucket domain name including the region name, please refer here for format. Note: The AWS CloudFront allows specifying S3 region-specific endpoint when creating S3 origin, it will prevent redirect issues from CloudFront to S3 Origin URL."
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_bucket_regional_domain_name
}
output "s3_bucket_hosted_zone_id" {
  description = "The Route 53 Hosted Zone ID for this bucket's region."
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_hosted_zone_id
}
output "s3_bucket_region" {
  description = "The AWS region this bucket resides in."
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_region
}
output "s3_bucket_website_endpoint" {
  description = "The website endpoint, if the bucket is configured with a website. If not, this will be an empty string."
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_website_endpoint
}
output "s3_bucket_website_domain" {
  description = "The domain of the website endpoint, if the bucket is configured with a website. If not, this will be an empty string. This is used to create Route 53 alias records. "
  value       = module.NAME_TEMPLATE_TO_REPLACE-store.this_s3_bucket_id
}

# --------------------------------------
# dynamodb

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = module.NAME_TEMPLATE_TO_REPLACE-lock.this_dynamodb_table_arn
}
output "dynamodb_table_id" {
  description = "ID of the DynamoDB table"
  value       = module.NAME_TEMPLATE_TO_REPLACE-lock.this_dynamodb_table_id
}
output "dynamodb_table_stream_arn" {
  description = "The ARN of the Table Stream. Only available when var.stream_enabled is true"
  value       = module.NAME_TEMPLATE_TO_REPLACE-lock.this_dynamodb_table_stream_arn
}
output "dynamodb_table_stream_label" {
  description = "A timestamp, in ISO 8601 format of the Table Stream. Only available when var.stream_enabled is true"
  value       = module.NAME_TEMPLATE_TO_REPLACE-lock.this_dynamodb_table_stream_label
}
