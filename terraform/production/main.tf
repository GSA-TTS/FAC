locals {
  cf_org_name      = "gsa-tts-oros-fac"
  cf_space_name    = "production"
  env              = "production"
  recursive_delete = true
}

module "database" {
  source = "../modules/database"

  cf_user          = var.cf_user
  cf_password      = var.cf_password
  cf_org_name      = local.cf_org_name
  cf_space_name    = local.cf_space_name
  app_name         = "fac"
  env              = local.env
  recursive_delete = local.recursive_delete
  rds_plan_name    = "micro-psql"
}