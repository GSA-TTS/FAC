module "sandbox" {
  source                  = "../shared/modules/sandbox"
  cf_space_name           = "sandbox"
  pgrst_jwt_secret        = var.pgrst_jwt_secret
  new_relic_license_key   = var.new_relic_license_key
  django_secret_login_key = var.django_secret_login_key
  sam_api_key             = var.sam_api_key
  login_client_id         = var.login_client_id
  login_secret_key        = var.login_secret_key
  branch_name             = var.branch_name
  backups_s3_id           = module.sandbox-backups-bucket.bucket_id
  cf_space_id             = data.cloudfoundry_space.space.id

  database_plan         = "medium-gp-psql"
  https_proxy_instances = 1
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
}

module "sandbox-backups-bucket" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v2.1.0"

  cf_space_id  = data.cloudfoundry_space.space.id
  name         = "backups"
  s3_plan_name = "basic"
  tags         = ["s3"]
}

# imports
import {
  to = module.sandbox.module.snapshot-database.cloudfoundry_service_instance.rds
  id = "c5f6bddd-77a8-4af1-a1c1-157c24a0920b"
}
import {
  to = module.sandbox.module.database.cloudfoundry_service_instance.rds
  id = "4f22d420-7be5-43b5-b298-bb73760b6aa8"
}

import {
  to = module.sandbox.module.s3-private.cloudfoundry_service_instance.bucket
  id = "d4da0886-ab87-40aa-a2c3-ce415e298752"
}

import {
  to = module.sandbox.module.s3-public.cloudfoundry_service_instance.bucket
  id = "24ab1bca-286e-4a4f-ae5d-3b46d7e6547c"
}

import {
  to = module.sandbox-backups-bucket.cloudfoundry_service_instance.bucket
  id = "a9785caf-cc2b-4135-a79f-819022933e00"
}

# Stuff used for apps in this space
data "cloudfoundry_org" "org" {
  name = var.cf_org_name
}

data "cloudfoundry_space" "space" {
  name = "sandbox"
  org  = data.cloudfoundry_org.org.id
}
