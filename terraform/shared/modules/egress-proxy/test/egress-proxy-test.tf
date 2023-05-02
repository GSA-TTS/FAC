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

# A test client app. This app doesn't actually do anything; it's static. We just
# need it to exist so that there's something for the module to look for in its
# clients list, and for which it can set up a network-policy.
data "external" "clientzip" {
  program = ["/bin/sh", "${path.module}/prepare-client.sh"]
}
resource "cloudfoundry_app" "test" {
  name             = "test"
  space            = data.cloudfoundry_space.client_space.id
  path             = data.external.clientzip.result.path
  source_code_hash = filesha256(data.external.clientzip.result.path)
  buildpack        = data.external.clientzip.result.buildpack
}

# Exercise the module under test
module "egress-proxy" {
  source = "./.."

  name          = "egress"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  client_space  = var.cf_space_name

  allowlist = {
    test = ["*.google.com:443", "*.login.gov:443", "gsa.gov:443"],
  }
  denylist = {
    test = ["mail.google.com:443", "verybad.login.gov:443"],
  }

  # Since there's no other way for Terraform to infer the dependency, this
  # ensures the test app exists before we try to configure the proxy to handle
  # it.
  depends_on = [
    cloudfoundry_app.test
  ]
}

data "external" "validate" {
  depends_on = [
    module.egress-proxy
  ]
  program = ["/bin/sh", "${path.module}/validate.sh"]
  query = {
    APPNAME   = "egress"
    ORGNAME   = var.cf_org_name
    SPACENAME = var.cf_space_name
  }
}

output "test-result" {
  value = data.external.validate.result.status
}
