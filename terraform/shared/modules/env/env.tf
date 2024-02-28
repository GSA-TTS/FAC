locals {
  module_versions = {
    database = "^8.x",
    s3       = "^8.x",
    clamav   = "^8.x"
  }
}

module "version" {
  for_each           = local.module_versions
  source             = "github.com/18f/terraform-cloudgov//semver"
  version_constraint = each.value
}

module "database" {
  source = "github.com/18f/terraform-cloudgov//database?ref=v${module.version["database"].target_version}"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-db"
  recursive_delete = var.recursive_delete
  tags             = ["rds"]
  rds_plan_name    = var.database_plan
}

module "s3-public" {
  source = "github.com/18f/terraform-cloudgov//s3?ref=v${module.version["s3"].target_version}"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-public-s3"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic-public"
  tags             = ["s3"]
}

module "s3-private" {
  source = "github.com/18f/terraform-cloudgov//s3?ref=v${module.version["s3"].target_version}"

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
