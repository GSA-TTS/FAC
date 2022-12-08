module "fac-dev" {
  source        = "../modules/fac"
  cf_space_name = "dev"

  database_plan    = "micro-psql"
  recursive_delete = true
}

