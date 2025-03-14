module "staging" {
  source                = "../shared/modules/env"
  cf_space_name         = "staging"
  cf_space_id           = data.cloudfoundry_space.space.id
  new_relic_license_key = var.new_relic_license_key
  new_relic_account_id  = var.new_relic_account_id
  new_relic_api_key     = var.new_relic_api_key
  pgrst_jwt_secret      = var.pgrst_jwt_secret

  database_plan         = "medium-gp-psql"
  postgrest_instances   = 1
  postgrest_memory      = 512
  swagger_instances     = 1
  https_proxy_instances = 1
  smtp_proxy_instances  = 1
  clamav_instances      = 1
  clamav_memory         = "2048M"
  clamav_fs_instances   = 1
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
}

module "staging-backups-bucket" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.2.0"

  cf_space_id  = data.cloudfoundry_space.space.id
  name         = "backups"
  s3_plan_name = "basic"
  tags         = ["s3"]
}

data "cloudfoundry_org" "org" {
  name = var.cf_org_name
}

data "cloudfoundry_space" "space" {
  name = "staging"
  org  = data.cloudfoundry_org.org.id
}
