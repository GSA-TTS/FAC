locals {
  scanner_name = "fac-file-scanner"
}

module "fac-file-scanner" {
  source            = "../scanner"
  name              = local.scanner_name
  cf_org_name       = var.cf_org_name
  cf_space_name     = var.cf_space_name
  https_proxy       = module.https-proxy.https_proxy
  db_id             = module.database.instance_id
  s3_id             = module.s3-private.bucket_id
  scanner_instances = 1
  scanner_memory    = 512
  disk_quota        = 512
}

resource "cloudfoundry_network_policy" "scanner-network-policy" {
  policy {
    source_app      = module.fac-file-scanner.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
  policy {
    source_app      = module.fac-file-scanner.app_id
    destination_app = module.clamav.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
