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

variable "postgrest_instances" {
  type        = number
  description = "the number of instances of the postgrest application to run (default: 2)"
  default     = 2
}

variable "swagger_instances" {
  type        = number
  description = "the number of instances of the swagger application to run (default: 2)"
  default     = 2
}

variable "https_proxy_instances" {
  type        = number
  description = "the number of instances of the HTTPS proxy application to run (default: 2)"
  default     = 2
}

variable "smtp_proxy_instances" {
  type        = number
  description = "the number of instances of the SMTP proxy application to run (default: 2)"
  default     = 2
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
  type        = string
  description = "the active API schemas being presented by PostgREST"
}

variable "clamav_image" {
  type        = string
  description = "the tag for the docker image"
}
