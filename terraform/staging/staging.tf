module "staging" {
  source                = "../shared/modules/env-base"
  cf_space_name         = "staging"
  new_relic_license_key = var.new_relic_license_key

  database_plan       = "medium-gp-psql"
  postgrest_instances = 1
  swagger_instances   = 1
  recursive_delete    = true
}

# module "staging-egress" {
#   source                = "../shared/modules/env-egress"
#   cf_space_name         = "staging"
#   https_proxy_instances = 1
#   recursive_delete      = true
# }
