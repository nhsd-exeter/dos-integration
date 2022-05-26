output "codestarconnection_arn" {
  description = "CodeStar Connection ARN"
  value       = aws_codestarconnections_connection.github.arn
}

output "integration_test_codebuild_stage" {
  description = "CodeBuild Integration Test Stages"
  value       = local.integration_make_targets
}
