variable "cf_org_name" {
  type        = string
  description = "name of the organization to configure"
  default     = "gsa-tts-oros-fac"
}

variable "cf_space_name" {
  type        = string
  description = "name of the space to configure"
  # No default... The calling module must supply this!
}

variable "database_plan" {
  type        = string
  description = "name of the cloud.gov RDS service plan name to create"
  # See https://cloud.gov/docs/services/relational-database/#plans
  default = "medium-gp-psql-redundant"
}

variable "recursive_delete" {
  type        = bool
  description = "when true, deletes service bindings attached to the resource (not recommended for production)"
  default     = false
}

# module "database" {
#   source = "../database"

#   cf_org_name      = var.cf_org_name
#   cf_space_name    = var.cf_space_name
#   name             = "fac-db"
#   recursive_delete = var.recursive_delete
#   rds_plan_name    = var.database_plan
# }

# module "s3" {
#   source = "../s3"

#   cf_org_name      = var.cf_org_name
#   cf_space_name    = var.cf_space_name
#   name             = "fac-public-s3"
#   recursive_delete = var.recursive_delete
#   s3_plan_name     = "basic-public"
# }
