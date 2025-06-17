variable "name" {
  type        = string
  description = "name of the fac application"
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

variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for app (eg firstname.lastname)"
}

variable "cf_space_id" {
  type        = string
  description = "cloud.gov space id for app"
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
}

variable "database_plan" {
  type        = string
  description = "name of the cloud.gov RDS service plan name to create"
  # See https://cloud.gov/docs/services/relational-database/#plans
  default = "medium-gp-psql-redundant"
}
