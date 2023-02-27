module "clamav" {
  source = "github.com/18f/terraform-cloudgov//clamav?ref=v0.3.0"

  # This generates eg "fac-av-staging.apps.internal", avoiding collisions with routes for other projects and spaces
  name           = "fac-av-${var.cf_space_name}"
  app_name_or_id = "gsa-fac"

  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  clamav_image  = "ajilaag/clamav-rest:20230224"
  max_file_size = "30M"
}

# module "database" {
#   source = ""github.com/18f/terraform-cloudgov//database""

#   cf_org_name      = var.cf_org_name
#   cf_space_name    = var.cf_space_name
#   name             = "${var.app_name}-db"
#   recursive_delete = var.recursive_delete
#   rds_plan_name    = var.database_plan
# }

# module "s3" {
#   source = "github.com/18f/terraform-cloudgov//s3"

#   cf_org_name      = var.cf_org_name
#   cf_space_name    = var.cf_space_name
#   name             = "${var.app_name}-public-s3"
#   recursive_delete = var.recursive_delete
# }
