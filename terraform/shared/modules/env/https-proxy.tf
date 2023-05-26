module "https-proxy" {
  source        = "../https-proxy"
  name          = "https-proxy"
  cf_org_name   = var.cf_org_name               # gsa-tts-oros-fac
  cf_space_name = "${var.cf_space_name}-egress" # eg prod-egress
  client_space  = var.cf_space_name             # eg prod
  instances     = var.https_proxy_instances

  # head of the "main" branch as of this commit
  gitref = "7487f882903b9e834a5133a883a88b16fb8b16c9"

  allowlist = {
    gsa-fac = [
      # SAM.gov API (https://open.gsa.gov/api/entity-api/)
      "api.sam.gov:443",

      # New Relic telemetry (https://docs.newrelic.com/docs/new-relic-solutions/get-started/networks/#data-ingest)
      # 
      # Note: New Relic says that APM agent data ingests via `collector*.newrelic.com`, but we can't specify that
      # to the Caddy forwardproxy (https://github.com/caddyserver/forwardproxy/blob/caddy2/README.md#access-control)
      # because it only allows subdomain wildcards in `*.` as a prefix. So this wildcard is a little broader than
      # we would prefer, but realistically the tightest domain mask we can specify given our current solution.
      # We put in an upstream issue about this: https://github.com/caddyserver/forwardproxy/issues/102
      "*.newrelic.com:443",

      # Login.gov sanbox
      "idp.int.identitysandbox.gov:443",
    ],
    # The parens here make Terraform understand that the key below is a reference
    # Solution from https://stackoverflow.com/a/57401750
    (local.clam_name) = ["database.clamav.net:443"],
  }
  denylist = {}
}
