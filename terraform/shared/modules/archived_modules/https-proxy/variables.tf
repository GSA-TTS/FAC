variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name for egress (eg staging-egress or prod-egress)"
}

variable "client_space" {
  type        = string
  description = "cloud.gov space name for client apps (eg staging or prod)"
}

variable "name" {
  type        = string
  description = "name of the egress proxy application"
}

variable "egress_memory" {
  type        = number
  description = "Memory in MB to allocate to egress proxy app"
  default     = 64
}

variable "gitref" {
  type        = string
  description = "gitref for the specific version of cg-egress-proxy that you want to use"
  default     = "refs/heads/main"
  # You can also specify a specific commit, eg "7487f882903b9e834a5133a883a88b16fb8b16c9"
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

variable "instances" {
  type        = number
  description = "the number of instances of the HTTPS proxy application to run (default: 2)"
  default     = 2
}
