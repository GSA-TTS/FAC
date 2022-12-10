variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name"
}

variable "name" {
  type        = string
  description = "Name of the database service instance"
}

variable "recursive_delete" {
  type        = bool
  description = "when true, deletes service bindings attached to the resource (not recommended for production)"
  default     = false
}

variable "rds_plan_name" {
  type        = string
  description = "service plan to use"
  # See options at https://cloud.gov/docs/services/relational-database/#plans
}
