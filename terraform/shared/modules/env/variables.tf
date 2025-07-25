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

variable "cf_space" {
  type        = object({ id = string, name = string })
  description = "cloud.gov space"
  # No default... The calling module knows which env is for which space and we
  # shouldn't assume it!
}

variable "database_plan" {
  type        = string
  description = "name of the cloud.gov RDS service plan name to create"
  # See https://cloud.gov/docs/services/relational-database/#plans
  default = "medium-gp-psql-redundant"
}

variable "postgrest_instances" {
  type        = number
  description = "the number of instances of the postgrest application to run (default: 2)"
  default     = 2
}

variable "postgrest_memory" {
  type        = string
  description = "the number of instances of the postgrest application to run (default: 2)"
  default     = "1024M"
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

variable "clamav_instances" {
  type        = number
  description = "the number of instances of the clamav application to run (default: 1)"
  default     = 1
}

variable "clamav_fs_instances" {
  type        = number
  description = "the number of instances of the clamav application to run (default: 1)"
  default     = 1
}

variable "clamav_memory" {
  type        = string
  description = "memory in MB to allocate to clamav app"
  default     = "3072M"
}

variable "new_relic_license_key" {
  type        = string
  description = "the license key to use when setting up the New Relic agent"
}

variable "pgrst_jwt_secret" {
  type        = string
  description = "the JWT signing secret for validating JWT tokens from api.data.gov"
}

variable "json_params" {
  type        = string
  description = "Optional parameters used for service instance (-c)"
}

variable "new_relic_account_id" {
  type        = number
  description = "New Relic Account ID"
}

variable "new_relic_api_key" {
  type        = string
  description = "New Relic API key"
}

variable "allowlist" {
  description = "Allowed egress for apps (applied first). A map where keys are app names, and the values are sets of acl strings."
  # See the upstream documentation for possible acl strings:
  #   https://github.com/caddyserver/forwardproxy/blob/caddy2/README.md#caddyfile-syntax-server-configuration
  type = map(set(string))
  default = {
    # appname    = [ "*.example.com:443", "example2.com:443" ]
  }
}

variable "denylist" {
  description = "Denied egress for apps (applied second). A map where keys are app names, and the values are sets of host:port strings."
  # See the upstream documentation for possible acl strings:
  #   https://github.com/caddyserver/forwardproxy/blob/caddy2/README.md#caddyfile-syntax-server-configuration
  type = map(set(string))
  default = {
    # appname    = [ "bad.example.com:443" ]
  }
}
