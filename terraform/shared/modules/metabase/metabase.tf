locals {
  app_id = cloudfoundry_app.metabase.id
  services = merge({

  }, var.service_bindings)
  metabase_version = "v0.59.2"
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
  space        = data.cloudfoundry_space.app_space.id
  domain       = data.cloudfoundry_domain.public.id
  host         = var.cf_space_name == "production" ? "metabase" : "metabase-${replace(var.cf_space_name, ".", "-")}"
  destinations = [{ app_id = cloudfoundry_app.metabase.id }]
  # Yields something like: fac-sandbox.app.cloud.gov
}

resource "cloudfoundry_app" "metabase" {
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
}
