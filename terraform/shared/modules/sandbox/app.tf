locals {
  app_name = "gsa-fac"
}

# TODO - Overhaul App Deploy
module "fac-app" {
  source                  = "../app"
  name                    = local.app_name
  cf_org_name             = var.cf_org_name
  cf_space_name           = var.cf_space_name
  https_proxy             = module.https-proxy.https_proxy
  https_proxy_creds_id    = cloudfoundry_service_instance.proxy_credentials.id
  new_relic_creds_id      = cloudfoundry_service_instance.newrelic_creds.id
  private_s3_id           = module.s3-private.bucket_id
  public_s3_id            = module.s3-public.bucket_id
  backups_s3_id           = var.backups_s3_id
  db_id                   = module.database.instance_id
  backup_db_id            = module.snapshot-database.instance_id
  app_instances           = 1
  app_memory              = 4096
  disk_quota              = 3072
  gitref                  = "refs/heads/${var.branch_name}"
  django_secret_login_key = var.django_secret_login_key
  sam_api_key             = var.sam_api_key
  login_client_id         = var.login_client_id
  login_secret_key        = var.login_secret_key
  depends_on = [ cloudfoundry_service_instance.newrelic_creds, module.https-proxy ]
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
