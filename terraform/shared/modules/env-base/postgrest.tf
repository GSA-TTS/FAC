locals {
  name = "postgrest"
}

resource "cloudfoundry_route" "postgrest" {
  space    = data.cloudfoundry_space.apps.id
  domain   = data.cloudfoundry_domain.public.id
  hostname = "fac-${var.cf_space_name}-${local.name}"
}

# Find the database service instance
# TODO: Use an output from the database module to get the database instance id
data "cloudfoundry_service" "rds" {
  name = "aws-rds"
}
data "cloudfoundry_service_instance" "database" {
  name_or_id = "fac-db"
  space      = data.cloudfoundry_space.apps.id
  depends_on = [
    module.database
  ]
}

resource "cloudfoundry_service_key" "postgrest" {
  name = "postgrest"
  #   service_instance = module.database.instance_id
  service_instance = data.cloudfoundry_service_instance.database.id
}

resource "cloudfoundry_app" "postgrest" {
  name         = local.name
  space        = data.cloudfoundry_space.apps.id
  docker_image = "postgrest/postgrest:v10.1.2"
  timeout      = 180
  memory       = 128
  disk_quota   = 256
  instances    = 2
  strategy     = "blue-green"
  routes {
    route = cloudfoundry_route.postgrest.id
  }
  environment = {
    PGRST_DB_URI : cloudfoundry_service_key.postgrest.credentials.uri
    PGRST_DB_SCHEMAS : "api"
    PGRST_DB_ANON_ROLE : "anon"
  }
}

