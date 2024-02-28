locals {
  module_versions = {
    database = "^0.8.0",
    s3       = "^0.8.0",
    clamav   = "^0.8.0"
  }
  database_version = "github.com/18f/terraform-cloudgov//database?ref=v${module.version["database"].target_version}"
  s3_version       = "github.com/18f/terraform-cloudgov//s3?ref=v${module.version["s3"].target_version}"
  clamav_version   = "github.com/18f/terraform-cloudgov//clamav?ref=v${module.version["clamav"].target_version}"
}

module "version" {
  for_each           = local.module_versions
  source             = "github.com/18f/terraform-cloudgov//semver"
  version_constraint = each.value
}

module "database" {
  source = local.database_version

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-db"
  recursive_delete = var.recursive_delete
  tags             = ["rds"]
  rds_plan_name    = var.database_plan
}

module "s3-public" {
  source = local.s3_version

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-public-s3"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic-public"
  tags             = ["s3"]
}

module "s3-private" {
  source = local.s3_version

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-private-s3"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic"
  tags             = ["s3"]
}

# Stuff used for apps in this space
data "cloudfoundry_space" "apps" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

data "cloudfoundry_domain" "private" {
  name = "apps.internal"
}
