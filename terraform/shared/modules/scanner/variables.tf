variable "name" {
  type        = string
  description = "name of the scanner application"
}

variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space" {
  type        = object({ id = string, name = string })
  description = "cloud.gov space"
}

variable "gitref" {
  type        = string
  description = "gitref for the specific version of scanner that you want to use"
  default     = "refs/heads/main"
  # You can also specify a specific commit, eg "7487f882903b9e834a5133a883a88b16fb8b16c9"
}

variable "scanner_memory" {
  type        = string
  description = "Memory in MB to allocate to scanner app instance"
  default     = "1046M"
}

variable "scanner_instances" {
  type        = number
  description = "the number of instances of the scanner app to run (default: 1)"
  default     = 1
}

variable "disk_quota" {
  type        = string
  description = "disk in MB to allocate to scanner app instance"
  default     = "512M"
}

variable "https_proxy" {
  type        = string
  description = "the full string of the https proxy for use with the logshipper app"
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
