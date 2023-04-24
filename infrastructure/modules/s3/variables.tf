variable "name" {
  description = "A descriptive name for the S3 instance"
}

variable "acl" {
  description = "The access control list assigned to this bucket"
  default     = null
}

variable "project_id" {
  description = "Project ID"
}

variable "bucket_iam_user" {
  description = "The name of the iam user assigned to the created s3 bucket"
  default     = ""
}

variable "force_destroy" {
  description = "Remove all objects in a bucket before destroying the bucket"
  default     = false
}

variable "tags" {
  description = "A map of tags to add to all resources"
  default     = {}
}

variable "versioning_enabled" {
  description = "If versioning is set for buckets in case of accidental deletion"
  default     = "true"
}

variable "lifecycle_infrequent_storage_transition_enabled" {
  description = "Specifies infrequent storage transition lifecycle rule status."
  default     = "false"
}

variable "lifecycle_infrequent_storage_object_prefix" {
  description = "Object key prefix identifying one or more objects to which the lifecycle rule applies."
  default     = ""
}

variable "lifecycle_days_to_infrequent_storage_transition" {
  description = "Specifies the number of days after object creation when it will be moved to standard infrequent access storage."
  default     = "60"
}

variable "lifecycle_glacier_transition_enabled" {
  description = "Specifies Glacier transition lifecycle rule status."
  default     = "false"
}

variable "lifecycle_glacier_object_prefix" {
  description = "Object key prefix identifying one or more objects to which the lifecycle rule applies."
  default     = ""
}

variable "lifecycle_days_to_glacier_transition" {
  description = "Specifies the number of days after object creation when it will be moved to Glacier storage."
  default     = "180"
}

variable "lifecycle_expiration_enabled" {
  description = "Specifies expiration lifecycle rule status."
  default     = "false"
}

variable "lifecycle_expiration_object_prefix" {
  description = "Object key prefix identifying one or more objects to which the lifecycle rule applies."
  default     = ""
}

variable "lifecycle_days_to_expiration" {
  description = "Specifies the number of days after object creation when the object expires."
  default     = "365"
}
variable "server_side_encryption_configuration" {
  description = "Specifies server-side encryption configuration for the bucket."

  default = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
}

variable "logging" {
  type    = map(string)
  default = {}
}

variable "attach_policy" {
  description = "Attach a policy to the bucket"
  default     = false
}
variable "policy" {
  description = "The policy to attach to the bucket"
  default     = ""
}

variable "control_object_ownership" {
  description = "Specifies whether Amazon S3 should require object ownership for requests to this bucket. If you specify this element in the request, Amazon S3 ignores it."
  default     = false
}

variable "object_ownership" {
  description = "Specifies whether Amazon S3 should require object ownership for requests to this bucket. If you specify this element in the request, Amazon S3 ignores it."
  default     = "BucketOwnerPreferred"
}
