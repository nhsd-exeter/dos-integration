output "codestarconnection_arn" {
  description = "CodeStar Connection ARN"
  value       = aws_codestarconnections_connection.github.arn
}
