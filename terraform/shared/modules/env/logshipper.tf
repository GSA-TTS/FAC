locals {
  logshipper_name = "cg-logshipper"
}

module "cg-logshipper" {
  source                = "../cg-logshipper"
  name                  = local.logshipper_name
  cf_org_name           = var.cf_org_name
  client_space          = var.cf_space_name
  new_relic_license_key = var.new_relic_license_key
  https_proxy           = module.https-proxy.https_proxy
}
