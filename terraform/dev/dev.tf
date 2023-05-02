module "dev" {
  source        = "../shared/modules/env-base"
  cf_space_name = "dev"

  database_plan    = "micro-psql"
  recursive_delete = true
}

module "dev-egress" {
  source           = "../shared/modules/env-egress"
  cf_space_name    = "dev"
  recursive_delete = true
}

