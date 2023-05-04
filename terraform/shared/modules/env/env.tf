locals {
  clam_name = "fac-av-${var.cf_space_name}"
}

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
      # 
      # Note: New Relic says that APM agent data ingests via `collector*.newrelic.com`, but we can't specify that
      # to the Caddy forwardproxy (https://github.com/caddyserver/forwardproxy/blob/caddy2/README.md#access-control)
      # because it only allows subdomain wildcards in `*.` as a prefix. So this wildcard is a little broader than
      # we would prefer, but realistically the tightest domain mask we can specify given our current solution.
      "*.newrelic.com:443",
    ],
    swagger = ["fac-${var.cf_space_name}-postgrest.app.cloud.gov:443"],
    # The parens here make Terraform understand that the key below is a reference
    # Solution from https://stackoverflow.com/a/57401750
    (local.clam_name) = ["database.clamav.net:443"],
  }
  denylist = {}
}

module "clamav" {
  source = "github.com/18f/terraform-cloudgov//clamav?ref=v0.5.1"

  # This generates eg "fac-av-staging.apps.internal", avoiding collisions with routes for other projects and spaces
  name           = local.clam_name
  app_name_or_id = "gsa-fac"

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  clamav_image  = "ajilaag/clamav-rest:20230228"
  max_file_size = "30M"
  https_proxy   = module.egress-proxy.https_proxy
}

module "database" {
  source = "github.com/18f/terraform-cloudgov//database?ref=v0.5.0"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-db"
  recursive_delete = var.recursive_delete
  rds_plan_name    = var.database_plan
}

module "s3-public" {
  source = "github.com/18f/terraform-cloudgov//s3"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-public-s3"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic-public"
}

module "s3-private" {
  source = "github.com/18f/terraform-cloudgov//s3"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-private-s3"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic"
}

# Stuff used for apps in this space
data "cloudfoundry_space" "apps" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

