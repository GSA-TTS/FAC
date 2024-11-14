module "staging" {
  source                = "../shared/modules/env"
  cf_space_name         = "staging"
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
  clamav_memory         = 2048
  clamav_fs_instances   = 1
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
}

module "staging-backups-bucket" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v1.1.0"

  cf_org_name   = var.cf_org_name
  cf_space_name = "staging"
  name          = "backups"
  s3_plan_name  = "basic"
  tags          = ["s3"]
}
