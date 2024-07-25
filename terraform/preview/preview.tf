module "preview" {
  source                = "../shared/modules/env"
  cf_space_name         = "preview"
  new_relic_license_key = var.new_relic_license_key
  new_relic_account_id  = var.new_relic_account_id
  new_relic_api_key     = var.new_relic_api_key
  pgrst_jwt_secret      = var.pgrst_jwt_secret

  database_plan         = "medium-gp-psql"
  postgrest_instances   = 1
  swagger_instances     = 1
  https_proxy_instances = 1
  smtp_proxy_instances  = 1
  clamav_instances      = 2
  clamav_fs_instances   = 1
  recursive_delete      = true
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
  cors_json = jsonencode(
    {
      "CORSRules" : [
        {
          "AllowedHeaders" : [
            "Authorization"
          ],
          "AllowedMethods" : [
            "HEAD",
            "GET"
          ],
          "AllowedOrigins" : [
            "https://fac-preview.app.cloud.gov"
          ],
          "ExposeHeaders" : [
            "ETag"
          ]
        }
      ]
    }
  )
}

module "preview-backups-bucket" {
  source = "github.com/gsa-tts/terraform-cloudgov//s3?ref=v0.9.1"

  cf_org_name   = var.cf_org_name
  cf_space_name = "preview"
  name          = "backups"
  s3_plan_name  = "basic"
  tags          = ["s3"]
}

import {
  to = module.preview.module.clamav.cloudfoundry_app.clamav_api
  id = "ed9b5108-1e31-44b8-9ba0-375e091c5589"
}
