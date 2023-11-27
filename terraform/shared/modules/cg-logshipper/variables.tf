variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for egress (eg staging-egress or prod-egress)"
}

variable "client_space" {
  type        = string
  description = "cloud.gov space name for client apps (eg staging or prod)"
}

variable "name" {
  type        = string
  description = "Name of the cg-logshipper application"
}

variable "logshipper_memory" {
  type        = number
  description = "Memory in MB to allocate to cg-logshipper app instance"
  default     = 1046
}

variable "logshipper_instances" {
  type        = number
  description = "the number of instances of the cg-logshipper app to run (default: 2)"
  default     = 1
}

variable "new_relic_license_key" {
  type        = string
  description = "the license key to use when setting up the New Relic agent"
}
