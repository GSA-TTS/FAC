module "metabase-app" {
  source        = "../metabase"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space.name
  cf_space_id   = var.cf_space.id
  name          = "metabase"
  app_memory    = "2048M"
  disk_quota    = "3072M"
  app_instances = 1
  buildpacks    = ["https://github.com/cloudfoundry/java-buildpack.git"]
  environment_variables = {
    ENV = var.cf_space.name
  }
  service_bindings = {
    "${module.database.database_name}"                        = ""
    "${module.metabasedb.database_name}"                      = ""
    "${cloudfoundry_service_instance.proxy_credentials.name}" = ""
  }
  depends_on = [module.metabasedb, module.database]
}

module "metabasedb" {
  source = "github.com/gsa-tts/terraform-cloudgov//database?ref=v2.5.0"

  cf_space_id   = var.cf_space.id
  name          = "metabase-db"
  tags          = ["rds"]
  rds_plan_name = var.database_plan
  json_params   = var.json_params
}
