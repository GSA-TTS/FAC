module "preview" {
  source                = "../shared/modules/env"
  cf_space_name         = "preview"
  new_relic_license_key = var.new_relic_license_key
  pgrst_jwt_secret      = var.pgrst_jwt_secret

  database_plan         = "medium-gp-psql"
  postgrest_instances   = 1
  swagger_instances     = 1
  https_proxy_instances = 1
  smtp_proxy_instances  = 1
  clamav_instances      = 2
  recursive_delete      = true
  json_params = jsonencode(
    {
      "storage" : 50,
    }
  )
}

import {
  to = module.preview.module.clamav.cloudfoundry_app.clamav_api
  id = "ed9b5108-1e31-44b8-9ba0-375e091c5589"
}
