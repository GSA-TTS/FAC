locals {
  logshipper_name = "logshipper"
}

module "logshipper" {
  # source      = "github.com/gsa-tts/terraform-cloudgov//logshipper?ref=v2.3.0"
  source      = "../cg-logshipper"
  name        = local.logshipper_name
  cf_org_name = var.cf_org_name
  https_proxy = module.https-proxy.https_proxy
  cf_space = {
    id   = var.cf_space.id
    name = var.cf_space.name
  }
  service_bindings = {
    "${cloudfoundry_service_instance.newrelic_creds.name}" = ""
  }
}
