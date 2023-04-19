module "staging" {
  source        = "../shared/modules/env-base"
  cf_space_name = "staging"

  database_plan    = "medium-gp-psql"
  recursive_delete = true
}

# module "staging-egress" {
#   source        = "../shared/modules/env-egress"
#   cf_space_name = "staging"
#   recursive_delete = true
# }
