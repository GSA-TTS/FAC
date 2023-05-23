variable "cf_user" {
  type        = string
  description = "cloud.gov deployer account user"
}

variable "cf_password" {
  type        = string
  description = "secret; cloud.gov deployer account password"
  sensitive   = true
}

variable "new_relic_license_key" {
  type        = string
  description = "the license key to use when setting up the New Relic agent"
}

variable "postgrest" {
  type        = string
  description = "the tag for the docker image"
}

variable "clamav" {
  type        = string
  description = "the tag for the docker image"
}
