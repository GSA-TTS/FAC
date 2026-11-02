locals {
  postgrest_name = "postgrest"
}

resource "cloudfoundry_route" "postgrest" {
  space        = data.cloudfoundry_space.space.id
  domain       = data.cloudfoundry_domain.public.id
  host         = "fac-${var.cf_space.name}-${local.postgrest_name}"
  destinations = [{ app_id = cloudfoundry_app.postgrest.id }]
}

data "docker_registry_image" "postgrest" {
  name = "ghcr.io/gsa-tts/fac/postgrest:latest"
}

resource "cloudfoundry_app" "postgrest" {
  name         = local.postgrest_name
  org_name     = data.cloudfoundry_org.org.name
  space_name   = var.cf_space.name
  docker_image = "ghcr.io/gsa-tts/fac/postgrest@${data.docker_registry_image.postgrest.sha256_digest}"
  timeout      = 180
  memory       = var.postgrest_memory
  disk_quota   = "256M"
  instances    = var.postgrest_instances
  strategy     = "rolling"
  environment = {
    # In Production and Preview we use a multi-host URI to put the read-replica first.
    # We have the full URI for each DB, but for the reformat we construct it from components.
    # Format: postgres://user:pass@replica.host:port,primary.host:port/dbname?options
    PGRST_DB_URI : var.cf_space.name == "production" || var.cf_space.name == "preview" ? format(
      "postgres://%s:%s@%s:%s,%s:%s/%s?%s",
      cloudfoundry_service_key.postgrest.credentials.username,
      cloudfoundry_service_key.postgrest.credentials.password,
      cloudfoundry_service_key.postgrest.credentials.replica_host,
      cloudfoundry_service_key.postgrest.credentials.port,
      cloudfoundry_service_key.postgrest.credentials.host,
      cloudfoundry_service_key.postgrest.credentials.port,
      cloudfoundry_service_key.postgrest.credentials.db_name,
      # `target_session_attrs` is for all requests except for some overrides, like LISTEN
      # Further params can be added by appending "&param=option"
      # See https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
      "target_session_attrs=read-only"
    ) : cloudfoundry_service_key.postgrest.credentials.uri
    PGRST_DB_SCHEMAS : "api_v1_1_0,api_v1_2_0,api_v1_3_0,api_v1_3_1,admin_api_v1_1_0"
    PGRST_DB_ANON_ROLE : "anon"
    PGRST_JWT_SECRET : var.pgrst_jwt_secret
    PGRST_DB_MAX_ROWS : 20000
  }
  service_bindings = [{ service_instance = module.cg-logshipper.syslog_drain_name }]
  depends_on       = [module.cg-logshipper]
}

# The following use the community provider as these have not been moved to the official provider.
# The community provider has upgraded to use the v3 API, however these resources should be moved to
# the official provider once they are supported.
resource "cloudfoundry_service_key" "postgrest" {
  provider         = cloudfoundry-community
  name             = "postgrest"
  service_instance = module.database.instance_id
}
