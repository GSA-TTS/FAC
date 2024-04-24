locals {
  scanner_name = "fac-scanner"
}

module "fac-file-scanner" {
  source            = "../scanner"
  name              = local.logshipper_name
  cf_org_name       = var.cf_org_name
  cf_space_name     = var.cf_space_name
  scanner_instances = 1
  scanner_memory    = 256
  disk_quota        = 256
}

resource "cloudfoundry_network_policy" "scanner-network-policy" {
  policy {
    source_app      = module.scanner_app.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
