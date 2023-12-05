locals {
  logshipper_name = "cg-logshipper"
}

module "cg-logshipper" {
  source                = "../cg-logshipper"
  name                  = local.logshipper_name
  cf_org_name           = var.cf_org_name   # gsa-tts-oros-fac
  cf_space_name         = var.cf_space_name # eg prod
  new_relic_license_key = var.new_relic_license_key
  https_proxy           = module.https-proxy.https_proxy
  logshipper_instances  = 1
  logshipper_memory     = 1046
  disk_quota            = 512
  new_relic_id          = cloudfoundry_user_provided_service.credentials.id
}
