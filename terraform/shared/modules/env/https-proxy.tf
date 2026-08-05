module "https-proxy" {
  source      = "github.com/GSA-TTS/cg-egress-proxy?ref=v1.1.0"
  name        = "https-proxy"
  cf_org_name = var.cf_org_name
  cf_egress_space = {
    id   = data.cloudfoundry_space.egress_space.id
    name = data.cloudfoundry_space.egress_space.name
  }
  instances = var.https_proxy_instances

  client_configuration = {
    "fac" = {
      ports = [443]
      allowlist = [
        "api.sam.gov",
        "*.newrelic.com",
        "idp.int.identitysandbox.gov",
        "secure.login.gov",
        "awscli.amazonaws.com",
        "database.clamav.net",
        "*.github.com",
        "release-assets.githubusercontent.com",
        "objects.githubusercontent.com"
      ]
    }
  }
}


resource "cloudfoundry_service_instance" "proxy_credentials" {
  name        = "https-proxy-creds"
  space       = var.cf_space.id
  type        = "user-provided"
  tags        = ["https-proxy-creds"]
  credentials = module.https-proxy.json_credentials
  depends_on  = [module.https-proxy]
}
