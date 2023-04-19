module "production" {
  source        = "../shared/modules/env-base"
  cf_space_name = "production"
}

# module "production-egress" {
#   source        = "../shared/modules/env-egress"
#   cf_space_name = "production"
# }
