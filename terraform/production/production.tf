module "production" {
  source = "../shared/modules/env"
  cf_space = {
    id   = data.cloudfoundry_space.space.id
    name = "production"
  }
  new_relic_license_key = var.new_relic_license_key
  new_relic_account_id  = var.new_relic_account_id
  new_relic_api_key     = var.new_relic_api_key
  pgrst_jwt_secret      = var.pgrst_jwt_secret
  clamav_instances      = 2
  clamav_fs_instances   = 1
  database_plan         = "xlarge-gp-psql-redundant"
  postgrest_instances   = 2
  json_params = jsonencode(
    {
      "storage" : 75,
    }
  )
}

# Note: The very first time we run apply in production, this will fail because
# the app it refers to, gsa-fac, doesn't exist yet; gsa-fac is deployed outside
# of Terraform. To address this, we should manage deployment of gsa-fac in
# Terraform.
module "domain" {
  source = "github.com/gsa-tts/terraform-cloudgov//domain?ref=v2.3.0"

  cf_org_name   = "gsa-tts-oros-fac"
  cf_space      = { id = data.cloudfoundry_space.space.id, name = "production" }
  app_ids       = [data.cloudfoundry_app.fac_app.id]
  cdn_plan_name = "domain"
  domain_name   = "fac.gov"
  host_name     = "app"
}

data "cloudfoundry_org" "org" {
  name = var.cf_org_name
}

data "cloudfoundry_space" "space" {
  name = "production"
  org  = data.cloudfoundry_org.org.id
}

data "cloudfoundry_app" "fac_app" {
  name       = "gsa-fac"
  space_name = "production"
  org_name   = var.cf_org_name
}
