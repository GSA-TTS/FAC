module "metabase" {
  count = var.cf_space.name == "staging" || var.cf_space.name == "production" ? 1 : 0

  source        = "../metabase"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space.name
  cf_space_id   = var.cf_space.id
  name          = "metabase"
  app_memory    = "4096M"
  disk_quota    = "4096M"
  db_plan       = var.metabase_database_plan
  db_params     = var.metabase_db_params
  app_instances = 1
  environment_variables = {
    ENV = var.cf_space.name
  }
  service_bindings = {
    "${cloudfoundry_service_instance.proxy_credentials.name}" = ""
  }
}
