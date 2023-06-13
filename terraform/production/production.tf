module "production" {
  source                = "../shared/modules/env"
  cf_space_name         = "production"
  new_relic_license_key = var.new_relic_license_key
  postgrest_image       = var.postgrest_image
  clamav_image          = var.clamav_image
}

module "domain" {
  source = "github.com/18f/terraform-cloudgov//domain?ref=v0.7.0"

  cf_org_name    = "gsa-tts-oros-fac"
  cf_space_name  = "production"
  app_name_or_id = "gsa-fac"
  cdn_plan_name  = "domain"
  domain_name    = "fac.gov"
  host_name      = "app
  depends_on = [
    module.production
  ]
}
