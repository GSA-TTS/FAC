variable "name" {
  type        = string
  description = "name of the fac application"
}

variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for app (eg firstname.lastname)"
}

variable "gitref" {
  type        = string
  description = "gitref for the specific version of app that you want to use"
  # default     = "refs/heads/main"
  # You can also specify a specific commit, eg "7487f882903b9e834a5133a883a88b16fb8b16c9"
}

variable "app_memory" {
  type        = string
  description = "Memory in MB to allocate to app app instance"
  default     = "2048M"
}

variable "app_instances" {
  type        = number
  description = "the number of instances of the app to run (default: 1)"
  default     = 1
}

variable "disk_quota" {
  type        = string
  description = "disk in MB to allocate to the app instance"
  default     = "2048M"
}

# variable "private_s3_id" {
#   type        = string
#   description = "the full string of the private s3 resource id"
# }

# variable "public_s3_id" {
#   type        = string
#   description = "the full string of the public s3 resource id"
# }

# variable "backups_s3_id" {
#   type        = string
#   description = "the full string of the backups s3 resource id"
# }

# variable "db_id" {
#   type        = string
#   description = "the full string of the core db resource id"
# }

# variable "backup_db_id" {
#   type        = string
#   description = "the full string of the backup db resource id"
# }
# # Can't be created before the app exists
# variable "https_proxy" {
#   type        = string
#   description = "the full string of the https proxy for use with the app"
# }

# variable "https_proxy_creds_id" {
#   type        = string
#   description = "the id of the credentials for the proxy to bind to the app"
# }

# variable "new_relic_creds_id" {
#   type        = string
#   description = "the id of the credentials for newrelic to bind to the app"
# }

variable "recursive_delete" {
  type        = bool
  description = "when true, deletes service bindings attached to the resource (not recommended for production)"
  default     = false
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

variable "route" {
  description = "The full app route (ie. 'myservice.apps.internal'). Defaults to '{var.name}.app.cloud.gov' if this is omitted"
  type        = string
  default     = null
}

variable "environment_variables" {
  description = "A map of environment values."
  type        = map(string)
}

# Example:
# service_bindings = {
#   my-service = "",
#   (module.my-other-service.name) = "",
#   yet-another-service = <<-EOT
#      {
#        "astring"     : "foo",
#        "anarray"     : ["bar", "baz"],
#        "anarrayobjs" : [
#          {
#            "name": "bat",
#            "value": "boz"
#        ],
#      }
#      EOT
#   }
# }
variable "service_bindings" {
  description = "A map of service instance name to JSON parameter string."
  type        = map(string)
}

variable "buildpacks" {
  description = "A list of buildpacks to add to the app resource."
  type        = list(string)
  default     = ["https://github.com/cloudfoundry/apt-buildpack.git", "https://github.com/cloudfoundry/python-buildpack.git"]
}
