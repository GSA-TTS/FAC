module "sandbox" {
  source                  = "../shared/modules/sandbox"
  cf_space_name           = "sandbox"
  pgrst_jwt_secret        = var.pgrst_jwt_secret
  new_relic_license_key   = var.new_relic_license_key
  django_secret_login_key = var.django_secret_login_key
  sam_api_key             = var.sam_api_key
  login_client_id         = var.login_client_id
  login_secret_key        = var.login_secret_key
  branch_name             = var.branch_name

  database_plan         = "medium-gp-psql"
  https_proxy_instances = 1
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
}
