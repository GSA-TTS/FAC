locals {
  logshipper_name = "logshipper"
}

module "cg-logshipper" {
  source               = "../cg-logshipper"
  name                 = local.logshipper_name
  cf_org_name          = var.cf_org_name
  cf_space_id          = var.cf_space_id
  cf_space_name        = var.cf_space_name
  https_proxy          = module.https-proxy.https_proxy
  logshipper_instances = 1
  logshipper_memory    = 256
  disk_quota           = 256
  new_relic_id         = cloudfoundry_user_provided_service.credentials.id
}

resource "cloudfoundry_network_policy" "logshipper-network-policy" {
  provider = cloudfoundry-community
  policy {
    source_app      = module.cg-logshipper.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
