# module "database" {
#   source = "../database"

#   cf_org_name      = var.cf_org_name
#   cf_space_name    = var.cf_space_name
#   name             = "${var.app_name}-db"
#   recursive_delete = var.recursive_delete
#   rds_plan_name    = var.database_plan
# }

# module "s3" {
#   source = "../s3"

#   cf_org_name      = var.cf_org_name
#   cf_space_name    = var.cf_space_name
#   name             = "${var.app_name}-public-s3"
#   recursive_delete = var.recursive_delete
#   s3_plan_name     = "basic-public"
# }
