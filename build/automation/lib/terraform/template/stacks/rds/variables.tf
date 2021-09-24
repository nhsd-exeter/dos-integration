# ==============================================================================
# User variables

variable "db_instance" {
  description = "The DB instance identifier name"
  default     = "test"
}
variable "db_port" {
  description = "The DB instance port number"
  default     = 5432
}
variable "db_name" {
  description = "The DB instance schema name"
  default     = "postgres"
}
variable "db_username" {
  description = "The DB instance username"
  default     = "postgres"
}
variable "db_password" {
  description = "The DB instance password"
  default     = "postgres"
}
