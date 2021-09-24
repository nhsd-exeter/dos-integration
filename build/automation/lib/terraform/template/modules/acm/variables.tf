# ==============================================================================
# Mandatory variables

variable "route53_zone_id" { description = "The ID of the hosted zone to contain this record" }
variable "cert_domain_name" { description = "A domain name for which the certificate should be issued" }
variable "cert_subject_alternative_names" { description = "A list of domains that should be SANs in the issued certificate" }

# ==============================================================================
# Context

variable "context" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }
