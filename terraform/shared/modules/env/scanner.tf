locals {
  scanner_name = "fac-file-scanner"
}

module "fac-file-scanner" {
  source      = "../scanner"
  name        = local.scanner_name
  cf_org_name = var.cf_org_name
  cf_space = {
    id   = var.cf_space.id
    name = var.cf_space.name
  }
  https_proxy       = module.https-proxy.https_proxy
  scanner_instances = 1
  scanner_memory    = "512M"
  disk_quota        = "512M"
  service_bindings = {
    "${module.s3-private.name}" = ""
    "${module.cg-logshipper.syslog_drain_name}" = ""
  }
  depends_on = [module.s3-private, module.cg-logshipper]
}
