locals {
  scanner_name = "fac-file-scanner"
}

data "cloudfoundry_app" "app" {
  name_or_id = local.clam_name
  space      = var.cf_space_name
}

data "cloudfoundry_service" "s3" {
  name = "fac-private-s3"
}

data "cloudfoundry_service" "rds" {
  name = "fac-db"
}
module "fac-file-scanner" {
  source            = "../scanner"
  name              = local.scanner_name
  cf_org_name       = var.cf_org_name
  cf_space_name     = var.cf_space_name
  https_proxy       = module.https-proxy.https_proxy
  clamav_id         = data.cloudfoundry_app.app.id
  db_id             = data.cloudfoundry_service.rds.id
  s3_id             = data.cloudfoundry_service.s3.id
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
}
