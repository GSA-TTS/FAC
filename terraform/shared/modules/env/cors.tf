locals {
  decoded_json = jsondecode(var.cors_json)
}
module "cors" {
  source        = "../cors"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  decoded_json  = local.decoded_json
  depends_on    = [module.s3-public]
}
