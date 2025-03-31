module "https-proxy" {
  source      = "github.com/GSA-TTS/terraform-cloudgov//egress_proxy?ref=v2.3.0"
  name        = "https-proxy"
  cf_org_name = var.cf_org_name
  cf_egress_space = {
    id   = data.cloudfoundry_space.egress_space.id
    name = data.cloudfoundry_space.egress_space.name
  }
  instances = var.https_proxy_instances
  allowlist = [
    "api.sam.gov:443",
    "*.newrelic.com:443",
    "${var.cf_org_name}-${var.cf_space.name}-egress-https-proxy.apps.internal",
    "idp.int.identitysandbox.gov:443",
    "secure.login.gov:443",
    "objects.githubusercontent.com:443",
    "awscli.amazonaws.com:443",
    "database.clamav.net:443"
  ]
}

# The following use the community provider as these have not been moved to the official provider.
# In the event that these resources do not get moved, the following will likely break
# and need to be rebuilt in a different method. In the event the v2 api gets an extended depreciation,
# these may continue to be used until the provider adds this functionality, in which case, should be
# upgraded as soon as possible.
resource "cloudfoundry_service_instance" "proxy_credentials" {
  name        = "https-proxy-creds"
  space       = var.cf_space.id
  type        = "user-provided"
  tags        = ["https-proxy-creds"]
  credentials = module.https-proxy.json_credentials
  depends_on  = [module.https-proxy]
}
