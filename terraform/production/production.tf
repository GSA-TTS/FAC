module "production" {
  source                = "../shared/modules/env"
  cf_space_name         = "production"
  new_relic_license_key = var.new_relic_license_key
  pgrst_jwt_secret      = var.pgrst_jwt_secret
}

# Note: The very first time we run apply in production, this will fail because
# the app it refers to, gsa-fac, doesn't exist yet; gsa-fac is deployed outside
# of Terraform. To address this, we should manage deployment of gsa-fac in
# Terraform.
module "domain" {
  source = "github.com/18f/terraform-cloudgov//domain?ref=v0.7.0"

  cf_org_name    = "gsa-tts-oros-fac"
  cf_space_name  = "production"
  app_name_or_id = "gsa-fac"
  cdn_plan_name  = "domain"
  domain_name    = "fac.gov"
  host_name      = "app"
}
