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

resource "cloudfoundry_route" "app_route" {
  space        = data.cloudfoundry_space.app_space.id
  domain       = data.cloudfoundry_domain.public.id
  host         = "metabase-${replace(var.cf_space_name, ".", "-")}"
  destinations = [{ app_id = cloudfoundry_app.metabase.id }]
  # Yields something like: fac-sandbox.app.cloud.gov
}

# data "external" "app_zip" {
#   program     = ["/bin/sh", "prepare_app.sh"]
#   working_dir = path.module
#   #   query = {
#   #     gitref = var.gitref
#   #   }
# }

locals {
  app_id = cloudfoundry_app.metabase.id
  services = merge({

  }, var.service_bindings)
}

data "docker_registry_image" "metabase" {
  name = "metabase/metabase:latest"
}

resource "cloudfoundry_app" "metabase" {
  name       = var.name
  space_name = var.cf_space_name
  org_name   = var.cf_org_name
  docker_image = "metabase/metabase@${data.docker_registry_image.metabase.sha256_digest}"
  #path             = "${path.module}/${data.external.app_zip.result.path}"
  #source_code_hash = filesha256("${path.module}/${data.external.app_zip.result.path}")
  #buildpacks                 = var.buildpacks

  memory                     = var.app_memory
  disk_quota                 = var.disk_quota
  instances                  = var.app_instances
  strategy                   = "rolling"
  health_check_type          = "http"
  health_check_http_endpoint = "/api/health"
  #command                    = "java --add-opens java.base/java.nio=ALL-UNNAMED -jar metabase.jar"
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
    SSL_CERT_FILE = "/etc/ssl/certs/ca-certificates.crt"
  }, var.environment_variables)
}
