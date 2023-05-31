locals {
  clam_name = "fac-av-${var.cf_space_name}"

}

module "database" {
  source = "github.com/18f/terraform-cloudgov//database?ref=v0.5.1"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-db"
  recursive_delete = var.recursive_delete
  rds_plan_name    = var.database_plan
}

module "s3-public" {
  source = "github.com/18f/terraform-cloudgov//s3?ref=v0.5.1"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-public-s3"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic-public"
}

module "s3-private" {
  source = "github.com/18f/terraform-cloudgov//s3?ref=v0.5.1"

  cf_org_name      = var.cf_org_name
  cf_space_name    = var.cf_space_name
  name             = "fac-private-s3"
  recursive_delete = var.recursive_delete
  s3_plan_name     = "basic"
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

