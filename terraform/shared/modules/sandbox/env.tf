module "database" {
  source = "github.com/gsa-tts/terraform-cloudgov//database?ref=v2.1.0"

  cf_space_id   = var.cf_space_id
  name          = "fac-db"
  tags          = ["rds"]
  rds_plan_name = var.database_plan
  json_params   = var.json_params
}

module "snapshot-database" {
  source = "github.com/gsa-tts/terraform-cloudgov//database?ref=v2.1.0"

  cf_space_id   = var.cf_space_id
  name          = "fac-snapshot-db"
  tags          = ["rds"]
  rds_plan_name = var.database_plan
  json_params   = var.json_params
}

module "s3-public" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.1.0"

  cf_space_id  = var.cf_space_id
  name         = "fac-public-s3"
  s3_plan_name = "basic-public"
  tags         = ["s3"]
}

module "s3-private" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.1.0"

  cf_space_id  = var.cf_space_id
  name         = "fac-private-s3"
  s3_plan_name = "basic"
  tags         = ["s3"]
}


# Stuff used for apps in this space
data "cloudfoundry_space" "apps" {
  provider = cloudfoundry-community
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

data "cloudfoundry_domain" "private" {
  name = "apps.internal"
}
