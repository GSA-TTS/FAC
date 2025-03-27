locals {
  app_name = "gsa-fac"
}

module "fac-app" {
  source                  = "../app"
  gitref                  = "refs/heads/${var.branch_name}"
  cf_org_name             = var.cf_org_name
  cf_space_name           = var.cf_space_name
  name                    = local.app_name
  app_memory              = "2048M"
  disk_quota              = "3072M"
  app_instances           = 1
  django_secret_login_key = var.django_secret_login_key
  sam_api_key             = var.sam_api_key
  login_client_id         = var.login_client_id
  login_secret_key        = var.login_secret_key
  environment_variables = {
    ENV                   = "SANDBOX"
    DISABLE_COLLECTSTATIC = 1
    DJANGO_BASE_URL       = "https://fac-${var.cf_space_name}.app.cloud.gov"
    AV_SCAN_URL           = "https://fac-av-${var.cf_space_name}.apps.internal:61443/scan"
    ALLOWED_HOSTS         = "fac-${var.cf_space_name}.app.cloud.gov"
  }
  service_bindings = {
    # We can use these with the 2.3.0 release of terraform-cloudgov
    # "${module.s3-private.bucket_name}" = ""
    # "${module.s3-private.bucket_name}" = ""
    # "${module.database.database_name}" = ""
    # "${module.snapshot-database.db_name}" = ""
    "fac-private-s3"                                          = ""
    "fac-public-s3"                                           = ""
    "fac-db"                                                  = ""
    "fac-snapshot-db"                                         = ""
    "${cloudfoundry_service_instance.newrelic_creds.name}"    = ""
    "${cloudfoundry_service_instance.proxy_credentials.name}" = ""
    "${module.logshipper.syslog_drain_name}"                  = ""
  }
  depends_on = [cloudfoundry_service_instance.newrelic_creds, module.https-proxy, module.logshipper]
}

# The following use the community provider as these have not been moved to the official provider.
# In the event that test items do not get moved, the following will likely break
# and need to be rebuilt in a different method. In the event the v2 api gets an extended depreciation,
# these may continue to be used until the provider adds this functionality, in which case, should be
# upgraded as soon as possible.
resource "cloudfoundry_network_policy" "app-network-policy" {
  provider = cloudfoundry-community

  policy {
    source_app      = module.fac-app.app_id
    destination_app = module.https-proxy.app_id
    port            = "61443"
    protocol        = "tcp"
  }
  policy {
    source_app      = module.fac-app.app_id
    destination_app = module.clamav.app_id
    port            = "61443"
    protocol        = "tcp"
  }
}
