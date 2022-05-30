output "codestarconnection_arn" {
  description = "CodeStar Connection ARN"
  value       = aws_codestarconnections_connection.github.arn
}

output "integration_test_make_targets" {
  description = "Integration Test Make Targets"
  value       = local.integration_make_targets
}
