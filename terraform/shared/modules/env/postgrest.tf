locals {
  postgrest_name = "postgrest"
  data_load_name = "dataload"
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

data "docker_registry_image" "postgrest" {
  name = "ghcr.io/gsa-tts/fac/postgrest:latest"
}

data "docker_registry_image" "data_load" {
  name = "ghcr.io/gsa-tts/fac-historic-public-csvs/load-historic-public-data:latest"
}

resource "cloudfoundry_app" "postgrest" {
  name         = local.postgrest_name
  space        = data.cloudfoundry_space.apps.id
  docker_image = "ghcr.io/gsa-tts/fac/postgrest@${data.docker_registry_image.postgrest.sha256_digest}"
  timeout      = 180
  memory       = 512
  disk_quota   = 256
  instances    = var.postgrest_instances
  strategy     = "rolling"
  routes {
    route = cloudfoundry_route.postgrest.id
  }

  environment = {
    PGRST_DB_URI : cloudfoundry_service_key.postgrest.credentials.uri
    PGRST_DB_SCHEMAS : "api_v1_0_0_beta"
    PGRST_DB_ANON_ROLE : "anon"
    PGRST_JWT_SECRET : var.pgrst_jwt_secret
    PGRST_DB_MAX_ROWS : 20000
  }
}

resource "cloudfoundry_app" "data_load" {
  name         = local.data_load_name
  space        = data.cloudfoundry_space.apps.id
  docker_image = "ghcr.io/gsa-tts/fac-historic-public-csvs/load-historic-public-data@${data.docker_registry_image.data_load.sha256_digest}"
  timeout      = 180
  memory       = 64
  disk_quota   = 64
  instances    = 1
  strategy     = "rolling"

  environment = {
    DATABASE_URL : cloudfoundry_service_key.postgrest.credentials.uri
  }
  depends_on = [
    cloudfoundry_app.postgrest
  ]
}
