module "cors" {
  source        = "../cors"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space_name
  string_json   = var.cors_json
  depends_on    = [module.s3-public]
}
