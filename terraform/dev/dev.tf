module "dev" {
  source                = "../shared/modules/env"
  cf_space_name         = "dev"
  new_relic_license_key = var.new_relic_license_key
  pgrst_jwt_secret      = var.pgrst_jwt_secret

  database_plan         = "micro-psql"
  postgrest_instances   = 1
  swagger_instances     = 1
  https_proxy_instances = 1
  smtp_proxy_instances  = 1
  recursive_delete      = true
}
