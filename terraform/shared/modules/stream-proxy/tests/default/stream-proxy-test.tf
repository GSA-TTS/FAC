terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.50.2"
    }
  }
}

variable "cf_org_name" {
  type = string
}
variable "cf_space_name" {
  type = string
}
variable "user" {
  type = string
}
variable "password" {
  type      = string
  sensitive = true
}

provider "cloudfoundry" {
  api_url  = "https://api.fr.cloud.gov"
  password = var.password
  user     = var.user
}

data "cloudfoundry_space" "client_space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

# A test client app. We need it to exist so that there's something for the
# module to look for in its clients list, and for which it can set up a
# network-policy.
data "external" "clientzip" {
  program = ["/bin/sh", "${path.module}/prepare-client.sh"]
}
resource "cloudfoundry_app" "stream-client" {
  name             = "stream-client"
  space            = data.cloudfoundry_space.client_space.id
  path             = data.external.clientzip.result.path
  source_code_hash = filesha256(data.external.clientzip.result.path)
  buildpacks       = split(",", data.external.clientzip.result.buildpacks)
  memory           = 128
}

data "cloudfoundry_domain" "default" {
  name = "apps.internal"
}

resource "cloudfoundry_route" "stream-client" {
  hostname = "${var.cf_org_name}-${replace(var.cf_space_name, ".", "-")}-stream-client"
  space    = data.cloudfoundry_space.client_space.id
  domain   = data.cloudfoundry_domain.default.id
  target {
    app = cloudfoundry_app.stream-client.id
  }
}

locals {
  urlpattern  = "(?:(?P<userinfo>[^@]+)@)?(?P<hostname>[^:]+)(?::(?P<port>\\d*))?"
  matches     = regex(local.urlpattern, cloudfoundry_route.stream-client.endpoint)
  proxydomain = local.matches.hostname
  proxyport   = 8080
}

# Exercise the module under test
module "stream-proxy" {
  source = "./../.."

  name          = "stream-proxy"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  client_space  = var.cf_space_name
  upstream      = "${local.proxydomain}:${local.proxyport}"
  clients       = ["stream-client"]
  instances     = 1
  depends_on = [
    cloudfoundry_route.stream-client
  ]
}

resource "cloudfoundry_network_policy" "connectback" {
  policy {
    source_app      = module.stream-proxy.app
    destination_app = cloudfoundry_app.stream-client.id_bg
    port            = "8080"
  }
}


data "external" "validate" {
  depends_on = [
    module.stream-proxy,
    cloudfoundry_app.stream-client,
    cloudfoundry_route.stream-client,
    cloudfoundry_network_policy.connectback,
  ]
  program = ["/bin/sh", "${path.module}/validate.sh"]
  query = {
    APPNAME    = "stream-proxy"
    CLIENTNAME = "stream-client"
    ORGNAME    = var.cf_org_name
    SPACENAME  = var.cf_space_name
  }
}

output "test-result" {
  value = data.external.validate.result.status
}
