# locals {
#   module_versions = {
#     database = "^0.x", # major version 0
#     s3       = "^0.x", # major version 0
#     clamav   = "^0.x"  # major version 0
#   }
# }

# module "version" {
#   for_each           = local.module_versions
#   source             = "github.com/18f/terraform-cloudgov//semver"
#   version_constraint = each.value
# }
