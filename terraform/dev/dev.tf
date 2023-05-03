module "dev" {
  source                = "../shared/modules/env-base"
  cf_space_name         = "dev"
  new_relic_license_key = var.new_relic_license_key

  database_plan       = "micro-psql"
  postgrest_instances = 1
  swagger_instances   = 1
  recursive_delete    = true
}

module "dev-egress" {
  source                = "../shared/modules/env-egress"
  cf_space_name         = "dev"
  https_proxy_instances = 1
  recursive_delete      = true
}

