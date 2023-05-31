locals {
  postgrest_name = "postgrest"
}

resource "cloudfoundry_route" "postgrest" {
  space    = data.cloudfoundry_space.apps.id
  domain   = data.cloudfoundry_domain.public.id
  hostname = "fac-${var.cf_space_name}-${local.postgrest_name}"
}

resource "cloudfoundry_service_key" "postgrest" {
  name             = "postgrest"
  service_instance = module.database.instance_id
}

resource "cloudfoundry_app" "postgrest" {
  name         = local.postgrest_name
  space        = data.cloudfoundry_space.apps.id
  docker_image = var.postgrest_image
  timeout      = 180
  memory       = 128
  disk_quota   = 256
  instances    = var.postgrest_instances
  strategy     = "rolling"
  routes {
    route = cloudfoundry_route.postgrest.id
  }

  environment = {
    PGRST_DB_URI : cloudfoundry_service_key.postgrest.credentials.uri
    PGRST_DB_SCHEMAS : "api"
    PGRST_DB_ANON_ROLE : "anon"
  }
}

