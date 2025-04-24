module "https-proxy" {
  source      = "github.com/GSA-TTS/terraform-cloudgov//egress_proxy?ref=v2.3.0"
  name        = "https-proxy"
  cf_org_name = var.cf_org_name
  cf_egress_space = {
    id   = data.cloudfoundry_space.egress_space.id
    name = data.cloudfoundry_space.egress_space.name
  }
  instances  = var.https_proxy_instances
  allowports = [443, 61443]
  allowlist = [
    "api.sam.gov:443",
    "*.newrelic.com:443",
    "${var.cf_org_name}-${var.cf_space.name}-egress-https-proxy.apps.internal",
    "idp.int.identitysandbox.gov:443",
    "secure.login.gov:443",
    "*.github.com:443",
    "objects.githubusercontent.com:443",
    "awscli.amazonaws.com:443",
    "database.clamav.net:443"
  ]
}

resource "cloudfoundry_service_instance" "proxy_credentials" {
  name        = "https-proxy-creds"
  space       = var.cf_space.id
  type        = "user-provided"
  tags        = ["https-proxy-creds"]
  credentials = module.https-proxy.json_credentials
  depends_on  = [module.https-proxy]
}
