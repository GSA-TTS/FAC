module "cors" {
  source        = "../cors"
  cf_org_name   = var.cf_org_name
  cf_space_name = var.cf_space.name
  depends_on    = [module.s3-public]
}
