locals {
  services = merge({
    "${module.database.database_name}" = ""
  }, var.service_bindings)

  metabase_version = "v0.63.16.7"
}

data "cloudfoundry_domain" "public" {
  name = "app.cloud.gov"
}

data "cloudfoundry_org" "app_org" {
  name = var.cf_org_name
}

data "cloudfoundry_space" "app_space" {
  name = var.cf_space_name
  org  = data.cloudfoundry_org.app_org.id
}

data "docker_registry_image" "metabase" {
  name = "metabase/metabase:${local.metabase_version}"
}

resource "cloudfoundry_route" "app_route" {
  space  = data.cloudfoundry_space.app_space.id
  domain = data.cloudfoundry_domain.public.id
  host   = var.cf_space_name == "production" ? "metabase" : "metabase-${replace(var.cf_space_name, ".", "-")}"
  # Yields something like: metabase-dev.app.cloud.gov
}

resource "cloudfoundry_app" "app" {
  name         = var.name
  space_name   = var.cf_space_name
  org_name     = var.cf_org_name
  docker_image = "metabase/metabase@${data.docker_registry_image.metabase.sha256_digest}"

  memory                     = var.app_memory
  disk_quota                 = var.disk_quota
  instances                  = var.app_instances
  strategy                   = "rolling"
  health_check_type          = "http"
  health_check_http_endpoint = "/api/health"
  command                    = <<-COMMAND
    MB_DB_CONNECTION_URI=$(echo "$VCAP_SERVICES" | grep -o '"uri":\s*"[^"]*' | sed 's/"uri":\s*//' | cut -d '"' -f2 | tail -1)
    export MB_DB_CONNECTION_URI

    ./app/run_metabase.sh
  COMMAND

  routes = [{
    route = cloudfoundry_route.app_route.url
    port  = "http1"
  }]

  service_bindings = [
    for service_name, params in local.services : {
      service_instance = service_name
      params           = (params == "" ? "{}" : params) # Empty string -> Minimal JSON
    }
  ]
  environment = merge({
    REQUESTS_CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"
    SSL_CERT_FILE      = "/etc/ssl/certs/ca-certificates.crt"
  }, var.environment_variables)

  depends_on = [module.database]
}

module "database" {
  source        = "github.com/gsa-tts/terraform-cloudgov//database?ref=v2.5.0"
  cf_space_id   = var.cf_space_id
  name          = "metabase-db"
  tags          = ["rds"]
  rds_plan_name = var.db_plan
  json_params   = var.db_params
}
