module "staging" {
  source        = "../shared/modules/base"
  cf_space_name = "staging"

  database_plan    = "medium-gp-psql"
  recursive_delete = true
}
