variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for client apps (eg staging or prod)"
}

variable "name" {
  type        = string
  description = "Name of the cg-logshipper application"
}

variable "gitref" {
  type        = string
  description = "gitref for the specific version of logshipper that you want to use"
  default     = "refs/heads/main"
  # You can also specify a specific commit, eg "7487f882903b9e834a5133a883a88b16fb8b16c9"
}

variable "disk_quota" {
  type        = number
  description = "disk in MB to allocate to cg-logshipper app instance"
  default     = 512
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

variable "https_proxy" {
  type        = string
  description = "the full string of the https proxy for use with the logshipper app"
}
