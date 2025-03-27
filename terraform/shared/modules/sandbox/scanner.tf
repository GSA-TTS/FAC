# service_instance = var.s3_id
# service_instance = var.logdrain_id

locals {
  scanner_name = "fac-file-scanner"
}

module "fac-file-scanner" {
  source            = "../scanner"
  name              = local.scanner_name
  cf_org_name       = var.cf_org_name
  cf_space = {
    id   = data.cloudfoundry_space.space.id
    name = var.cf_space_name
  }
  https_proxy       = module.https-proxy.https_proxy
  scanner_instances = 1
  scanner_memory    = "512M"
  disk_quota        = "512M"
  service_bindings = {
    # "${module.s3-private.name}" = ""
    "fac-private-s3"                         = ""
    "${module.logshipper.syslog_drain_name}" = ""
  }
  depends_on = [module.s3-private, module.logshipper]
}

# The following use the community provider as these have not been moved to the official provider.
# In the event that these resources do not get moved, the following will likely break
# and need to be rebuilt in a different method. In the event the v2 api gets an extended depreciation,
# these may continue to be used until the provider adds this functionality, in which case, should be
# upgraded as soon as possible.
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
