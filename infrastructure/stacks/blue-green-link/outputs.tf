output "connected_blue_green_environment" {
  value       = var.blue_green_environment
  description = "The name of the blue/green environment that is connected to the shared resources."
}

output "previous_blue_green_environment" {
  value       = var.previous_blue_green_environment
  description = "The name of the blue/green environment that was previously connected to the shared resources."
}
