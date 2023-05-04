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
  }
  denylist = {}
}

module "clamav" {
  source = "github.com/18f/terraform-cloudgov//clamav?ref=v0.3.0"

  # This generates eg "fac-av-staging.apps.internal", avoiding collisions with routes for other projects and spaces
  name           = "fac-av-${var.cf_space_name}"
  app_name_or_id = "gsa-fac"

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  clamav_image  = "ajilaag/clamav-rest:20230228"
  max_file_size = "30M"
}

module "database" {
  source = "github.com/18f/terraform-cloudgov//database"

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

# Find the database service instance, so we can get keys for it and give the
# resulting creds to the docker apps as environment variables
#
# TODO: Use an output from the database module to get the database instance id
# and just use that directly. Can do that once this PR is merged!
# https://github.com/18F/terraform-cloudgov/pull/10
data "cloudfoundry_service" "rds" {
  name = "aws-rds"
}
data "cloudfoundry_service_instance" "database" {
  name_or_id = "fac-db"
  space      = data.cloudfoundry_space.apps.id
  depends_on = [
    module.database
  ]
}

resource "cloudfoundry_user_provided_service" "credentials" {
  name  = "newrelic-creds"
  space = data.cloudfoundry_space.apps.id
  credentials = {
    "NEW_RELIC_LICENSE_KEY" = var.new_relic_license_key
  }
}