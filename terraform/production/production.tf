module "production" {
  source                = "../shared/modules/env"
  cf_space_name         = "production"
  new_relic_license_key = var.new_relic_license_key
  postgrest_image       = var.postgrest_image
  clamav_image          = var.clamav_image
}
