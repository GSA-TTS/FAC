module "staging" {
  source                = "../shared/modules/env"
  cf_space_name         = "staging"
  new_relic_license_key = var.new_relic_license_key
  postgrest_image       = var.postgrest_image
  clamav_image          = var.clamav_image

  database_plan         = "medium-gp-psql"
  postgrest_instances   = 1
  swagger_instances     = 1
  https_proxy_instances = 1
  smtp_proxy_instances  = 1
  recursive_delete      = true
}

