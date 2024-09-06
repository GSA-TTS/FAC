module "sandbox" {
  source                = "../shared/modules/sandbox"
  cf_space_name         = var.cf_space_name
  pgrst_jwt_secret      = var.pgrst_jwt_secret
  new_relic_license_key = var.new_relic_license_key

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
