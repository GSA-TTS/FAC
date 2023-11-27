locals {
  logshipper_name = "cg-logshipper"
}

module "cg-logshipper" {
  source                = "../cg-logshipper"
  name                  = local.logshipper_name
  cf_org_name           = var.cf_org_name   # gsa-tts-oros-fac
  cf_space_name         = var.cf_space_name # eg prod-egress
  client_space          = var.cf_space_name # eg prod
  new_relic_license_key = var.new_relic_license_key
  https_proxy           = module.https-proxy.https_proxy
}
