module "fac-staging" {
  source        = "../modules/fac"
  cf_space_name = "staging"

  database_plan    = "medium-gp-psql"
  recursive_delete = true
}
