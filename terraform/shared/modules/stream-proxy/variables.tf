variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for the proxy (eg staging-egress or prod-egress)"
}

variable "client_space" {
  type        = string
  description = "cloud.gov space name for client apps (eg staging or prod)"
}

variable "name" {
  type        = string
  description = "name of the proxy application"
}

variable "memory" {
  type        = number
  description = "Memory in MB to allocate to the proxy app"
  default     = 64
}

variable "upstream" {
  type        = string
  description = "Upstream sevice to which client connections will be routed of the form somedomain:someport. Defaults to smtp-relay.gmail.com:587"
  default     = "smtp-relay.gmail.com:587"
}

variable "clients" {
  description = "Permitted clients. A set of app names or IDs. If empty, network policies won't be created."
  type        = set(string)
  default = [
    # "app1", cloudfoundry_app.foo.id 
  ]
}

variable "instances" {
  type        = number
  description = "the number of instances of the proxy application to run (default: 2)"
  default     = 2
}
