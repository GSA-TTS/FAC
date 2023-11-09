variable "cf_user" {
  type        = string
  description = "cloud.gov deployer account user"
}

variable "cf_password" {
  type        = string
  description = "secret; cloud.gov deployer account password"
  sensitive   = true
}

variable "populate_creds_locally" {
  type        = bool
  description = "whether to create files for working with the environment locally; specify true during local development"
  default     = false
}
