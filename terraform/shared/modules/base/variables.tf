# These variables expose what is open for customization in an environment. Where
# there are defaults, they are the production defaults.
# 
# Example usage:
# 
# For production:
#   module "production" {
#     source        = "../shared/modules/base"
#     cf_space_name = "production"
#     # No further customization needed
#   }
# 
# For dev:
#   module "dev" {
#     cf_space_name = "dev"
#     database_plan    = "micro-psql"
#     recursive_delete = true
#   }


variable "cf_org_name" {
  type        = string
  description = "name of the organization to configure"
  default     = "gsa-tts-oros-fac"
}

variable "cf_space_name" {
  type        = string
  description = "name of the space to configure"
  # No default... The calling module knows which env is for which space and we
  # shouldn't assume it!
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
