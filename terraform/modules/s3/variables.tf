variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name (staging or prod)"
}

variable "recursive_delete" {
  type        = bool
  description = "when true, deletes service bindings attached to the resource (not recommended for production)"
  default     = false
}

variable "name" {
  type        = string
  description = "name of the cloud.gov service instance"
}

variable "s3_plan_name" {
  type        = string
  description = "service plan to use"
  default     = "basic"
  # See options at https://cloud.gov/docs/services/s3/#plans
}
