variable "name" {
  type        = string
  description = "name of the scanner application"
}

variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for scanner (eg production)"
}

variable "gitref" {
  type        = string
  description = "gitref for the specific version of scanner that you want to use"
  default     = "refs/heads/main"
  # You can also specify a specific commit, eg "7487f882903b9e834a5133a883a88b16fb8b16c9"
}

variable "scanner_memory" {
  type        = number
  description = "Memory in MB to allocate to scanner app instance"
  default     = 1046
}

variable "scanner_instances" {
  type        = number
  description = "the number of instances of the scanner app to run (default: 1)"
  default     = 1
}


variable "disk_quota" {
  type        = number
  description = "disk in MB to allocate to cg-logshipper app instance"
  default     = 512
}

variable "clamav_id" {
  type        = string
  description = "the full string of the clamav api resource id"
}

variable "s3_id" {
  type        = string
  description = "the full string of the s3 resource id"
}

variable "db_id" {
  type        = string
  description = "the full string of the database resource id"
}
