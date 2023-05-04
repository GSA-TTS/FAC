
module "egress-proxy" {
  source                = "../egress-proxy"
  name                  = "egress"
  cf_org_name           = var.cf_org_name               # gsa-tts-oros-fac
  cf_space_name         = "${var.cf_space_name}-egress" # eg prod-egress
  client_space          = var.cf_space_name             # eg prod
  https_proxy_instances = var.https_proxy_instances

  # head of the "main" branch as of this commit
  gitref = "7487f882903b9e834a5133a883a88b16fb8b16c9"

  allowlist = {
    gsa-fac = [
      # SAM.gov API (https://open.gsa.gov/api/entity-api/)
      "api.sam.gov:443",

      # New Relic telemetry (https://docs.newrelic.com/docs/new-relic-solutions/get-started/networks/#data-ingest)
      "collector*.newrelic.com:443", "*-api.newrelic.com:443"
    ],
  }
  denylist = {}
}

