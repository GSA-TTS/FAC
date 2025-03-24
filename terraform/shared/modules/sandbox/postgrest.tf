locals {
  postgrest_name = "postgrest"
}

resource "cloudfoundry_route" "postgrest" {
  space  = data.cloudfoundry_space.space.id
  domain = data.cloudfoundry_domain.public.id
  host   = "fac-${var.cf_space_name}-${local.postgrest_name}"
  destinations = [{app_id = cloudfoundry_app.postgrest.id}]
}

resource "cloudfoundry_service_key" "postgrest" {
  provider         = cloudfoundry-community
  name             = "postgrest"
  service_instance = module.database.instance_id
}

data "docker_registry_image" "postgrest" {
  name = "ghcr.io/gsa-tts/fac/postgrest:latest"
}

resource "cloudfoundry_app" "postgrest" {
  name         = local.postgrest_name
  org_name     = data.cloudfoundry_org.org.name
  space_name   = data.cloudfoundry_space.space.name
  docker_image = "ghcr.io/gsa-tts/fac/postgrest@${data.docker_registry_image.postgrest.sha256_digest}"
  timeout      = 180
  memory       = "1024M"
  disk_quota   = "256M"
  instances    = var.postgrest_instances
  strategy     = "rolling"
  environment = {
    PGRST_DB_URI : cloudfoundry_service_key.postgrest.credentials.uri,
    PGRST_DB_SCHEMAS : "api_v1_0_3,api_v1_1_0,admin_api_v1_1_0",
    PGRST_DB_ANON_ROLE : "anon",
    PGRST_JWT_SECRET : var.pgrst_jwt_secret,
    PGRST_DB_MAX_ROWS : 20000
  }
}
