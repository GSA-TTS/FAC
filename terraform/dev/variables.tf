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

variable "postgrest_image" {
  type        = string
  description = "the tag for the docker image"
}

variable "postgrest_db_schemas" {
  type = string
  description = "the active API schemas being presented by PostgREST"
}

variable "clamav_image" {
  type        = string
  description = "the tag for the docker image"
}
