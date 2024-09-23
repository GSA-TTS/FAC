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
  type        = number
  description = "memory in MB to allocate to clamav app"
  default     = 2048
}

variable "pgrst_jwt_secret" {
  type        = string
  description = "the JWT signing secret for validating JWT tokens from api.data.gov"
}

variable "json_params" {
  type        = string
  description = "Optional parameters used for service instance (-c)"
}

variable "new_relic_license_key" {
  type        = string
  description = "the license key to use when setting up the New Relic agent"
}

variable "gitref" {
  type        = string
  description = "gitref for the specific version of scanner that you want to use"
  default     = "refs/heads/main"
  # You can also specify a specific commit, eg "7487f882903b9e834a5133a883a88b16fb8b16c9"
}

variable "sam_api_key" {
  type = string
}
variable "django_secret_login_key" {
  type = string
}
variable "login_client_id" {
  type = string
}
variable "login_secret_key" {
  type = string
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
