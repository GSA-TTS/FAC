module "dev" {
  source                = "../shared/modules/env"
  cf_space_name         = "dev"
  new_relic_license_key = var.new_relic_license_key
  new_relic_account_id  = var.new_relic_account_id
  new_relic_api_key     = var.new_relic_api_key
  pgrst_jwt_secret      = var.pgrst_jwt_secret

  database_plan         = "medium-gp-psql"
  postgrest_instances   = 1
  swagger_instances     = 1
  https_proxy_instances = 1
  smtp_proxy_instances  = 1
  clamav_instances      = 1
  clamav_fs_instances   = 1
  recursive_delete      = true
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
}

module "dev-backups-bucket" {
  source = "github.com/18f/terraform-cloudgov//s3?ref=v0.9.1"

  cf_org_name   = var.cf_org_name
  cf_space_name = "dev"
  name          = "backups"
  s3_plan_name  = "basic"
  tags          = ["s3"]
}
