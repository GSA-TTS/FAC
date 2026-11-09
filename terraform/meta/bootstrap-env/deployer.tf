locals {
  deployer_service_instance = "${var.name}-deployer"
  deployer_service_key      = "${local.deployer_service_instance}-key"
}

data "cloudfoundry_service_plan" "service_account" {
  service_offering_name = "cloud-gov-service-account"
  name                  = "space-deployer"
}

resource "cloudfoundry_service_instance" "space_deployer" {
  name         = local.deployer_service_instance
  space        = cloudfoundry_space.space.id
  type         = "managed"
  service_plan = data.cloudfoundry_service_plan.service_account.id
  # We shouldn't attempt to manage service instances before we know that the space
  # permissions allow us to do that.
  depends_on = [
    cloudfoundry_space_role.developer,
    cloudfoundry_space_role.manager
  ]
}
