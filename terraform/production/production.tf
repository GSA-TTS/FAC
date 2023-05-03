module "production" {
  source                = "../shared/modules/env-base"
  cf_space_name         = "production"
  new_relic_license_key = var.new_relic_license_key
}

# module "production-egress" {
#   source        = "../shared/modules/env-egress"
#   cf_space_name = "production"
# }
