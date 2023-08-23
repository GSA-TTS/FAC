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

data "docker_registry_image" "postgrest" {
  name = "ghcr.io/gsa-tts/fac/postgrest:latest"
}

resource "cloudfoundry_app" "postgrest" {
  name         = local.postgrest_name
  space        = data.cloudfoundry_space.apps.id
  docker_image = "ghcr.io/gsa-tts/fac/postgrest@${data.docker_registry_image.postgrest.sha256_digest}"
  timeout      = 180
  memory       = 1024
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
    PGRST_DB_MAX_ROWS : 1000
  }
}

