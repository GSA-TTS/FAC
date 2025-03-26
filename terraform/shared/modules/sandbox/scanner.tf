# service_instance = var.s3_id
# service_instance = var.logdrain_id

locals {
  scanner_name = "fac-file-scanner"
}

module "fac-file-scanner" {
  source            = "../scanner"
  name              = local.scanner_name
  cf_org_name       = var.cf_org_name
  cf_space_name     = var.cf_space_name
  https_proxy       = module.https-proxy.https_proxy
  scanner_instances = 1
  scanner_memory    = "512M"
  disk_quota        = "512M"
  service_bindings = {
    # "${module.s3-private.name}" = ""
    # ${module.logdrain.syslog_drain_name} = ""
    "fac-private-s3" = ""
    # "logdrain" = ""
  }
}

resource "cloudfoundry_network_policy" "scanner-network-policy" {
  provider = cloudfoundry-community
  policy {
    source_app      = module.fac-file-scanner.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
  policy {
    source_app      = module.fac-file-scanner.app_id
    destination_app = module.file_scanner_clamav.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
