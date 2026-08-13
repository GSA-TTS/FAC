locals {
  deployer_service_instance = "${var.name}-deployer"
  deployer_service_key      = "${local.deployer_service_instance}-key"
}

# The following use the community provider as these have not been moved to the official provider.
# The community provider has upgraded to use the v3 API, however these resources should be moved to
# the official provider once they are supported.
data "cloudfoundry_service" "service_account" {
  provider = cloudfoundry-community
  name     = "cloud-gov-service-account"
}

resource "cloudfoundry_service_instance" "space_deployer" {
  name         = local.deployer_service_instance
  space        = cloudfoundry_space.space.id
  type         = "managed"
  service_plan = data.cloudfoundry_service.service_account.service_plans["space-deployer"]
  # We shouldn't attempt to manage service instances before we know that the space
  # permissions allow us to do that.
  depends_on = [
    cloudfoundry_space_users.space_permissions
  ]
}
