module "dev" {
  source        = "../shared/modules/base"
  cf_space_name = "dev"

  database_plan    = "micro-psql"
  recursive_delete = true
}

