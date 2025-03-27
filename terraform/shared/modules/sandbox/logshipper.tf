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
    id   = data.cloudfoundry_space.space.id
    name = var.cf_space_name
  }
  service_bindings = {
    "${cloudfoundry_service_instance.newrelic_creds.name}" = ""
  }
}

# The following use the community provider as these have not been moved to the official provider.
# In the event that these resources do not get moved, the following will likely break
# and need to be rebuilt in a different method. In the event the v2 api gets an extended depreciation,
# these may continue to be used until the provider adds this functionality, in which case, should be
# upgraded as soon as possible.
resource "cloudfoundry_network_policy" "logshipper-network-policy" {
  provider = cloudfoundry-community
  policy {
    source_app      = module.logshipper.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
